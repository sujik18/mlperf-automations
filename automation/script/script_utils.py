import os
import mlc.utils as utils
from utils import compare_versions

def get_variation_and_script_tags(tags_string):

    tags = [] if tags_string == '' else tags_string.split(',')

    script_tags = []
    variation_tags = []

    for t in tags:
        t = t.strip()
        if t != '':
            if t.startswith('_'):
                tx = t[1:]
                if tx not in variation_tags:
                    variation_tags.append(tx)
            elif t.startswith('-_'):
                tx = '-' + t[2:]
                if tx not in variation_tags:
                    variation_tags.append(tx)
            else:
                script_tags.append(t)
    return {'return': 0, 'script_tags': script_tags,
            'variation_tags': variation_tags}


def select_script_and_cache(
    self,
    i,
    script_tags,
    variation_tags,
    parsed_script_alias,
    quiet,
    skip_remembered_selections=False,
    force_cache=False,
    force_skip_cache=False,
):
    """
    Search scripts by tags, resolve ambiguity, apply cache pruning,
    select a script (quiet or interactive), and return pruned cache entries.
    """

    logger = self.logger
    recursion_spaces = self.recursion_spaces

    # ---------------------------------------------------------
    # STEP 1: Script search
    ii = {
        "script_tags": script_tags,
        "variation_tags": variation_tags,
        "out": None,
    }
    for key in ["automation", "artifact", "item", "details"]:
        if i.get(key):
            ii[key] = i[key]

    r = self.search(ii)
    if r["return"] > 0:
        return r

    list_of_found_scripts = r["list"]
    script_tags_string = ",".join(script_tags)

    # ---------------------------------------------------------
    # STEP 2: Report found scripts
    mlc_script_info = i.get("script_call_prefix", "").strip() or "mlcr "
    if not mlc_script_info.endswith(" "):
        mlc_script_info += " "

    if parsed_script_alias:
        mlc_script_info += parsed_script_alias + '"'

    if script_tags or variation_tags:
        if script_tags:
            mlc_script_info += script_tags_string
        if variation_tags:
            if script_tags:
                mlc_script_info += ","
            mlc_script_info += ",".join("_" + v for v in variation_tags)

    logger.info(recursion_spaces + "* " + mlc_script_info)

    # ---------------------------------------------------------
    # STEP 3: Error handling
    if not r["found_scripts"]:
        return {
            "return": 1,
            "error": f"no scripts were found with tags: {script_tags} (when variations ignored)",
        }

    if not list_of_found_scripts:
        return {
            "return": 16,
            "error": f"no scripts were found with tags: {script_tags}\n{r.get('warning', '')}",
        }

    if (
        len(list_of_found_scripts) > 1
        and script_tags_string == ""
        and parsed_script_alias
        and "?" not in parsed_script_alias
        and "*" not in parsed_script_alias
    ):
        msg = (
            "Ambiguity in the following scripts have the same UID:\n"
            + "\n".join(" * " + s.path for s in list_of_found_scripts)
        )
        return {"return": 1, "error": msg}

    # ---------------------------------------------------------
    # STEP 4: Sort deterministically
    list_of_found_scripts = sorted(
        list_of_found_scripts,
        key=lambda s: (s.meta.get("sort", 0), s.path),
    )

    # ---------------------------------------------------------
    # STEP 5: Apply remembered selection
    if not skip_remembered_selections and len(list_of_found_scripts) > 1:
        for sel in self.remembered_selections:
            if (
                sel["type"] == "script"
                and set(sel["tags"].split(",")) == set(script_tags_string.split(","))
            ):
                list_of_found_scripts = [sel["cached_script"]]
                break

    # ---------------------------------------------------------
    # STEP 6: Determine if cache preload is needed
    preload_cached_scripts = any(
        s.meta.get("cache", False)
        or (s.meta.get("can_force_cache", False) and force_cache)
        for s in list_of_found_scripts
    )

    cache_list = []

    # STEP: cache handling
    cache_list = []

    if should_preload_cache(list_of_found_scripts,
                            force_cache) and not force_skip_cache:
        rc = search_script_cache(
            self.cache_action,
            script_tags_string,
            variation_tags,
            recursion_spaces,
            logger,
        )
        if rc["return"] > 0:
            return rc

        cache_list = rc["cache_list"]

        rc = prune_scripts_using_cache(list_of_found_scripts, cache_list)
        if rc["return"] > 0:
            return rc

        list_of_found_scripts = rc["scripts"]
        cache_list = rc["cache_list"]

    # STEP: select script (unchanged)
    if len(list_of_found_scripts) > 1:
        selected_index = select_script_item(
            list_of_found_scripts,
            "script",
            recursion_spaces,
            False,
            script_tags_string,
            quiet,
            logger,
        )
    else:
        selected_index = 0

    selected_script = list_of_found_scripts[selected_index]

    # STEP: prune cache to selected script
    cache_list = prune_cache_for_selected_script(cache_list, selected_script)

    return {
        "return": 0,
        "script": selected_script,
        "scripts": list_of_found_scripts,
        "cache_list": cache_list,
    }


def select_script_item(lst, text, recursion_spaces,
                       can_skip, script_tags_string, quiet, logger=None):
    """
    Internal: select script
    """

    string1 = recursion_spaces + \
        '    - More than 1 {} found for "{}":'.format(text, script_tags_string)

    if not logger:
        return {'return': 1, 'error': 'No logger provided'}

    # If quiet, select 0 (can be sorted for determinism)
    if quiet:
        logger.debug(string1)
        logger.debug('Selected default due to "quiet" mode')

        return 0

    # Select 1 and proceed
    logger.info(string1)
    num = 0

    for a in lst:
        meta = a.meta

        name = meta.get('name', '')

        s = a.path
        if name != '':
            s = '"' + name + '" ' + s

        x = recursion_spaces + \
            '      {}) {} ({})'.format(num, s, ','.join(meta['tags']))

        version = meta.get('version', '')
        if version != '':
            x += ' (Version {})'.format(version)

        logger.info(x)
        num += 1

    s = 'Make your selection or press Enter for 0'
    if can_skip:
        s += ' or use -1 to skip'

    x = input(recursion_spaces + '      ' + s + ': ')
    x = x.strip()
    if x == '':
        x = '0'

    selection = int(x)

    if selection < 0 and not can_skip:
        selection = 0

    if selection < 0:
        logger.info(recursion_spaces + '      Skipped')
    else:
        if selection >= num:
            selection = 0
        logger.info(
            recursion_spaces +
            '      Selected {}: {}'.format(
                selection,
                lst[selection].path))

    return selection


def should_preload_cache(scripts, force_cache=False):
    """
    Return True if at least one script requires or allows caching.
    """
    for script in scripts:
        if script.meta.get("cache", False):
            return True
        if script.meta.get("can_force_cache", False) and force_cache:
            return True
    return False


def search_script_cache(
    cache_action,
    script_tags_string,
    variation_tags,
    recursion_spaces,
    logger,
):
    """
    Search cache entries for given script & variation tags.
    """
    cache_tags = "-tmp"

    if script_tags_string:
        cache_tags += "," + script_tags_string

    if variation_tags:
        cache_tags += ",_" + ",_".join(variation_tags)

    # Fix variation exclusion syntax
    cache_tags = cache_tags.replace(",_-", ",-_")

    logger.debug(
        recursion_spaces +
        f"  - Searching for cached script outputs with tags: {cache_tags}"
    )

    rc = cache_action.access(
        {
            "action": "search",
            "target_name": "cache",
            "tags": cache_tags,
        }
    )

    if rc["return"] > 0:
        return rc

    return {
        "return": 0,
        "cache_list": rc["list"],
    }


def prune_scripts_using_cache(scripts, cache_list):
    """
    Retain only scripts that have matching cache entries.
    """
    pruned_scripts = []

    for cache_entry in cache_list:
        assoc = cache_entry.meta.get("associated_script_item", "")
        if "," not in assoc:
            return {
                "return": 1,
                "error": f'MLC artifact format is wrong "{assoc}" - no comma found',
            }

        uid = assoc.split(",", 1)[1]
        cache_entry.meta["associated_script_item_uid"] = uid

        for script in scripts:
            if script.meta.get("uid") == uid and script not in pruned_scripts:
                pruned_scripts.append(script)

    # Avoid over-pruning
    if pruned_scripts:
        scripts = pruned_scripts

    return {
        "return": 0,
        "scripts": scripts,
        "cache_list": cache_list,
    }


def prune_cache_for_selected_script(cache_list, selected_script):
    """
    Keep only cache entries associated with selected script.
    """
    selected_uid = selected_script.meta["uid"]

    return [
        c for c in cache_list
        if c.meta.get("associated_script_item_uid") == selected_uid
    ]


def check_versions(action_object, cached_script_version,
                   version_min, version_max):
    """
    Internal: check versions of the cached script

    If cached_script_version is less than version_min or greater than version_max,
        return True to skip using the cached script
    """
    skip_cached_script = False

    if cached_script_version != '':
        if version_min != '':
            ry = compare_versions({
                'version1': cached_script_version,
                'version2': version_min})
            if ry['return'] > 0:
                return ry

            if ry['comparison'] < 0:
                skip_cached_script = True

        if not skip_cached_script and version_max != '':
            ry = compare_versions({
                'version1': cached_script_version,
                'version2': version_max})
            if ry['return'] > 0:
                return ry

            if ry['comparison'] > 0:
                skip_cached_script = True

    return skip_cached_script


def get_version_tag_from_version(version, cached_tags):
    tags_to_add = []
    if version != '':
        version = str(version)
        if 'version-' + version not in cached_tags:
            cached_tags.append('version-' + version)
        if '-git-' in version:
            version_without_git_commit = version.split("-git-")[0]
            if 'version-' + version_without_git_commit not in cached_tags:
                cached_tags.append('version-' + version_without_git_commit)
    return {'return': 0}


def prepare_cache_tags(ctx):
    '''
    Prepare cache tags for searching and creating cache entries
    '''
    ctx.logger.debug(
        ctx.recursion_spaces +
        f'  - Preparing cache tags...'
    )
    cached_tags = []
    explicit_cached_tags = []

    # Create a search query to find that we already ran this script with the same or similar input
    # It will be gradually enhanced with more "knowledge"  ...

    # script tags
    if len(ctx.script_tags) > 0:
        for x in ctx.script_tags:
            if x not in cached_tags:
                cached_tags.append(x)

    # found tags
    if len(ctx.found_script_tags) > 0:
        for x in ctx.found_script_tags:
            if x not in cached_tags:
                cached_tags.append(x)

    explicit_cached_tags = cached_tags.copy()

    # explicit variations
    if len(ctx.explicit_variation_tags) > 0:
        explicit_variation_tags_string = ''

        for t in ctx.explicit_variation_tags:
            if explicit_variation_tags_string != '':
                explicit_variation_tags_string += ','
            if t.startswith("-"):
                x = "-_" + t[1:]
            else:
                x = '_' + t
            explicit_variation_tags_string += x

            if x not in explicit_cached_tags:
                explicit_cached_tags.append(x)

        ctx.logger.debug(
            ctx.recursion_spaces +
            '    - Prepared explicit variations: {}'.format(explicit_variation_tags_string))

    # normal variations
    if len(ctx.variation_tags) > 0:
        variation_tags_string = ''

        for t in ctx.variation_tags:
            if variation_tags_string != '':
                variation_tags_string += ','
            if t.startswith("-"):
                x = "-_" + t[1:]
            else:
                x = '_' + t
            variation_tags_string += x

            if x not in cached_tags:
                cached_tags.append(x)

        ctx.logger.debug(
            ctx.recursion_spaces +
            '    - Prepared variations: {}'.format(variation_tags_string))

    # version tags
    r = get_version_tag_from_version(ctx.version, cached_tags)
    if r['return'] > 0:
        return r

    r = get_version_tag_from_version(ctx.version, explicit_cached_tags)
    if r['return'] > 0:
        return r

    # Add extra cache tags (such as "virtual" for python)
    if len(ctx.extra_cache_tags) > 0:
        for t in ctx.extra_cache_tags:
            if t not in cached_tags:
                cached_tags.append(t)
                explicit_cached_tags.append(t)

    # env-driven tags
    # Add tags from deps (will be also duplicated when creating new cache entry)
    extra_cache_tags_from_env = ctx.meta.get('extra_cache_tags_from_env', [])
    for extra_cache_tags in extra_cache_tags_from_env:
        key = extra_cache_tags['env']
        prefix = extra_cache_tags.get('prefix', '')

        v = ctx.env.get(key, '').strip()
        if v != '':
            for t in v.split(','):
                x = 'deps-' + prefix + t
                if x not in cached_tags:
                    cached_tags.append(x)
                    explicit_cached_tags.append(x)

    return cached_tags, explicit_cached_tags


def search_cache(ctx, explicit_cached_tags):
    '''
    Search for cached script outputs based on prepared cache tags
    '''
    search_tags = '-tmp'
    if len(explicit_cached_tags) > 0:
        search_tags += ',' + ','.join(explicit_cached_tags)

    ctx.logger.debug(
        ctx.recursion_spaces +
        '    - Searching for cached script outputs with the following tags: {}'.format(search_tags))

    r = ctx.self.cache_action.access({
        'action': 'search',
        'target_name': 'cache',
        'tags': search_tags
    })
    if r['return'] > 0:
        return r

    return search_tags, r['list']


def apply_remembered_cache_selection(ctx, search_tags, found_cached_scripts):
    '''
    Apply remembered cache selection if any
    '''
    if ctx.skip_remembered_selections or len(found_cached_scripts) <= 1:
        ctx.logger.debug(
            ctx.recursion_spaces +
            f'  - Skipping remembered cache selections...'
        )
        return found_cached_scripts

    for selection in ctx.remembered_selections:
        if selection['type'] == 'cache' and set(selection['tags'].split(',')) == set(search_tags.split(',')):
            tmp_version_in_cached_script = selection['cached_script'].meta.get('version', '')
            skip_cached_script = check_versions(
                ctx.self.action_object,
                tmp_version_in_cached_script,
                ctx.version_min,
                ctx.version_max
            )
            if skip_cached_script:
                return {'return': 2, 'error': 'The version of the previously remembered selection for a given script ({}) mismatches the newly requested one'.format(
                    tmp_version_in_cached_script)}
            else:
                found_cached_scripts = [selection['cached_script']]
                ctx.logger.debug(
                    ctx.recursion_spaces +
                    '  - Found remembered selection with tags "{}"!'.format(search_tags))
                return [selection['cached_script']]
            
    return found_cached_scripts


def validate_cached_scripts(ctx, found_cached_scripts):
    '''
    Validate found cached scripts and return only valid ones
    '''
    valid = []
    if len(found_cached_scripts) > 0:
        for cached_script in found_cached_scripts:
            if is_cached_entry_valid(ctx, cached_script):
                ctx.logger.debug(
                    ctx.recursion_spaces + 
                    f'  - Validated cached entry: {cached_script.path}'
                )
                valid.append(cached_script)

    return valid


def is_cached_entry_valid(ctx, cached_script):
    '''
    Validate a cached script entry
    Returns True if valid, False otherwise
    '''
    # Check dependent paths
    if not validate_dependent_paths(ctx, cached_script):
        return False
    
    # Run validate_cache script if present
    detected_version = run_validate_cache_if_present(ctx, cached_script)
    # Get cached version
    cached_version = cached_script.meta.get('version', '')

    if cached_version and detected_version and cached_version != detected_version:
        # Cached version mismatch
        return False
    
    # check_versions returns True if cache should be skipped
    return not check_versions(
        ctx.self.action_object,
        cached_version,
        ctx.version_min,
        ctx.version_max
    )


def validate_dependent_paths(ctx, cached_script):
    '''
    Validate dependent paths for a cached script entry
    Returns True if all dependent paths are present, False otherwise
    '''
    dependent_paths = []

    # single dependent path
    dependent_cached_path = cached_script.meta.get('dependent_cached_path')
    if dependent_cached_path:
        dependent_paths.append(dependent_cached_path)

    # multiple dependent paths (colon-separated)
    dependent_cached_paths = cached_script.meta.get('dependent_cached_paths', '').split(':')
    dependent_paths += [p for p in dependent_cached_paths if p]

    if not dependent_paths:
        return True

    for dep in dependent_paths:
        if os.path.exists(dep):
            continue
        
        # TODO Need to restrict the below check to within container
        # env
        ctx.env['tmp_dep_cached_path'] = dep
        from script import docker_utils
        r = docker_utils.get_container_path_script(ctx.env)
        if not os.path.exists(r.get('value_env', '')):
            ctx.logger.debug(
                ctx.recursion_spaces +
                f'  - Skipping cached entry as dependent path is missing: {r.get("value_env")}'
            )
            return False

    return True


def run_validate_cache_if_present(ctx, cached_script):
    '''
    Run validate_cache script if present in the script directory
    Returns detected version if validation passes, None otherwise
    '''
    import copy

    ctx.logger.debug(
        ctx.recursion_spaces +
        f'  - Validating cached entry: {cached_script.path}'
    )
    os_info = ctx.self.os_info
    # Bat extension for this host OS
    bat_ext = os_info['bat_ext']
    script_path = ctx.found_script_path

    validate_script = os.path.join(script_path, f'validate_cache{bat_ext}')
    if not os.path.exists(validate_script):
        return None

    # reconstruct env/state from cached metadata
    env_tmp = copy.deepcopy(ctx.env)
    state_tmp = copy.deepcopy(ctx.state)

    path_to_cached_state_file = os.path.join(
        cached_script.path,
        ctx.self.file_with_cached_state
    )

    r = utils.load_json(file_name=path_to_cached_state_file)
    if r['return'] > 0:
        return None

    cached_meta = r.get("meta")
    if not cached_meta:
        return None
    new_env = cached_meta.get("new_env", {})
    if new_env:
        env_tmp.update(new_env)
    new_state = cached_meta.get("new_state", {})
    if new_state:
        state_tmp.update(new_state)

    # re-run deps
    deps = ctx.meta.get('deps')
    if deps:
        r = ctx.self._call_run_deps(
            deps,
            ctx.self.local_env_keys,
            ctx.meta.get('local_env_keys', []),
            ctx.recursion_spaces + ctx.extra_recursion_spaces,
            ctx.remembered_selections,
            ctx.variation_tags_string,
            True,
            '',
            ctx.show_time,
            ctx.extra_recursion_spaces,
            {}
        )
        if r['return'] > 0:
            return None

    run_script_input = {
        'path': script_path,
        'bat_ext': bat_ext,
        'os_info': os_info,
        'recursion_spaces': ctx.recursion_spaces,
        'tmp_file_run': ctx.self.tmp_file_run,
        'self': ctx.self,
        'meta': ctx.meta,
        'customize_code': ctx.customize_code,
        'customize_common_input': ctx.customize_common_input,
    }

    r = ctx.self.run_native_script({
        'run_script_input': run_script_input,
        'env': env_tmp,
        'script_name': 'validate_cache',
        'detect_version': True
    })

    if r['return'] > 0:
        return None

    return r.get('version')