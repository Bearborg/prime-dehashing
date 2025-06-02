--This file contains a variety of SQL snippets that I've found useful when querying the resource db.


-- Display match stats
with const as (select 'MP1/1.00' as game, null as pak),
meta as (
	select count(distinct(hash)) as total_assets from const, asset_usages us
	where us.game = const.game
	and iif(const.pak is not null, us.pak = const.pak COLLATE NOCASE, 1)
),
match_groups as (
	select au.type, ap.path_matches as matches, count(distinct au.hash) as hits
	from const, asset_paths ap
	inner join asset_usages au on ap.hash = au.hash
	where au.game = const.game
	and iif(const.pak is not null, au.pak = const.pak COLLATE NOCASE, 1)
	group by au.type, ap.path_matches
)
select coalesce(unmatched.type, matched.type) as type,
coalesce(matched.hits, 0) as matched,
coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0) as all_assets,
round((100.00 * coalesce(matched.hits, 0)) / max((coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0)), 1), 2) as pct_matched
,round(100.00 * (coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0)) / meta.total_assets, 2) as pct_of_total
from (
	select 2 as order_num, type, hits from match_groups where matches = 0
	union all
	select 1 as order_num, 'Total' as type, sum(hits) as hits from match_groups where matches = 0
) as unmatched
full outer join (
	select 2 as order_num, type, hits from match_groups where matches = 1
	union all
	select 1 as order_num, 'Total' as type, sum(hits) as hits from match_groups where matches = 1
) as matched on matched.type = unmatched.type
, meta
order by coalesce(unmatched.order_num, matched.order_num), coalesce(unmatched.type, matched.type)

--Missing files
select ar.game, ar.source, us.type, ar.target from asset_references ar
left join assets on ar.target = assets.hash
inner join asset_usages us on ar.source = us.hash and us.game = ar.game
where assets.hash is NULL
group by ar.target, us.game
order by ar.game, us.type, target

--fetch all deps
select ap2.path || IIF(ap2.path_matches, '', '!!') as path, ap2.hash, us.type
from asset_paths ap
inner join asset_references ar on ar.source = ap.hash
inner join asset_usages us on us.hash = ar.target
inner join asset_paths ap2 on ap2.hash = ar.target
where ap.hash = '76A743BC' COLLATE NOCASE
--and us.game = 'MP1/1.00'
group by ap2.hash
order by us.type, ap2.path

--fetch all refs
select ap2.path || IIF(ap2.path_matches, '', '!!') as path, ap2.hash, us.type
from asset_paths ap
inner join asset_references ar on ar.target = ap.hash
inner join asset_usages us on us.hash = ar.source
inner join asset_paths ap2 on ap2.hash = ar.source
where ap.hash = '681f3907' COLLATE NOCASE
--and us.game = 'MP2/NTSC'
group by ap2.hash
order by us.type, ap2.path

--Matches by pak and type
select * from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
where ap.path_matches = 0
and us.game like 'MP1/1.00'
--and us.pak = 'MiscData.pak' COLLATE NOCASE
and us.type = 'ANIM'
group by ap.hash
order by us.pak, ap.path

--Nearby unmatched PARTs
select ap.hash, ap2.path from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
inner join asset_references ar on ar.source = ap.hash
inner join asset_paths ap2 on ap2.hash = ar.target
inner join asset_usages us2 on ap2.hash = us2.hash
where ap.path_matches = 0 and ap2.path_matches = 1
and us.game like 'MP1/1.00'
and us.type = 'PART'
and us2.type = 'PART'
group by us2.hash
order by ap.hash

--particle textures
select ap.hash, ap2.path from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
inner join asset_references ar on ar.target = ap.hash
inner join asset_paths ap2 on ap2.hash = ar.source
inner join asset_usages us2 on ap2.hash = us2.hash
where ap.path_matches = 0
and us.game like 'MP1/1.00'
and us.type = 'TXTR'
and us2.type in ('PART', 'SWHC', 'CRSC', 'DPSC', 'WPSC')
group by ap.hash
order by ap.path

--Nearby unmatched ANIMs
select ap.hash, ap.path, ap2.path from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
inner join asset_references ar on ar.target = ap.hash
inner join asset_paths ap2 on ap2.hash = ar.source
inner join asset_usages us2 on ap2.hash = us2.hash
where ap.path_matches = 0 and ap2.path_matches = 1
and us.game like 'MP1/1.00'
and us.type = 'ANIM'
and us2.type = 'ANCS'
group by ap.hash
order by ap2.path

--Nearby unmatched models
select ap.hash, ap.path, ap2.path from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
inner join asset_references ar on ar.target = ap.hash
inner join asset_paths ap2 on ap2.hash = ar.source
inner join asset_usages us2 on ap2.hash = us2.hash
where ap.path_matches = 0 and ap2.path_matches = 1
and us.game like 'MP1/1.00'
and us.type in ('CMDL', 'CSKR', 'CINF')
and us2.type = 'ANCS'
group by ap.hash
order by ap2.path

--Unmatched room names
select * from asset_paths ap
inner join asset_usages us on ap.hash = us.hash
where ap.path_matches = 0
and us.game like 'MP1%'
and ap.path like '%Strings/English/Worlds%' COLLATE NOCASE
and us.type = 'STRG'
group by ap.hash
order by ap.path

--Name but no path
select assets.*, MAX(us.name), MAX(us.type), group_concat(us.game, ','), group_concat(us.pak, ',') from assets
inner join asset_usages us on assets.hash = us.hash
left join asset_paths ap on assets.hash = ap.hash 
where coalesce(ap.path_matches, 0) = 0
GROUP BY assets.hash
HAVING SUM(us.name is not null) > 0 and SUM(us.game like 'MP1/1.00') > 0
order by MAX(us.type), MAX(us.name);

--Unmatched MP1 SCANs
select assets.*, MAX(us.name), ap.path, group_concat(us.game, ','), group_concat(us.pak, ',') from assets
inner join asset_usages us on assets.hash = us.hash
left join asset_paths ap on assets.hash = ap.hash 
where coalesce(ap.path_matches, 0) = 0
GROUP BY assets.hash
HAVING SUM(us.game like 'MP1%') > 0 and MAX(us.type) = 'SCAN' order by path;

--Unmatched scan images
select assets.*, ap.path from assets
inner join asset_usages us on assets.hash = us.hash
left join asset_paths ap on assets.hash = ap.hash 
where coalesce(ap.path_matches, 0) = 0
GROUP BY assets.hash
HAVING SUM(us.game like 'MP1%') > 0 and MAX(us.type) = 'TXTR' and ap.path like '$/ScannableObjects%' order by path;

--Type collisions
select assets.*, group_concat(us.type, ',') from assets
inner join asset_usages us on assets.hash = us.hash
GROUP BY assets.hash
HAVING count(distinct type) <> 1;

--Missing from paths
select assets.hash, MAX(us.name), MAX(us.type), group_concat(us.game, ','), group_concat(us.pak, ',') from assets
left join asset_usages us on assets.hash = us.hash
left join asset_paths ap on assets.hash = ap.hash
where ap.path is null
GROUP BY assets.hash

--MPR-only strings
with scans as
(
select ap.hash as hash, ap.path as path, ap.path_matches as path_matches from asset_paths ap
inner join asset_usages au on au.hash = ap.hash
where au.type = 'STRG'
group by ap.hash having SUM(au.game <> 'MPR') = 0
)
select 'Total' as hash, '' as path, round(100.00 * SUM(scans.path_matches) / COUNT(hash), 2) as path_matches from scans
UNION ALL
select * from scans where path_matches <> 1 order by path_matches desc, path asc

--Unmatched MP1/2 shared files
select assets.*, ap.path, group_concat(us.game, ','), group_concat(us.pak, ',')  from assets
inner join asset_usages us on assets.hash = us.hash
inner join asset_paths ap on assets.hash = ap.hash 
where ap.path_matches = 0
GROUP BY assets.hash
HAVING SUM(us.game = 'MP1/1.00') > 0 and SUM(us.game = 'MP2/NTSC') > 0 
order by ap.path;

--MP2 $/Worlds matches
select ap.hash as hash, ap.path as path, ap.path_matches as path_matches from asset_paths ap
inner join asset_usages au on au.hash = ap.hash
where au.game like 'MP2%' and ap.path like '$/worlds/%' and ap.path_matches = 1 group by ap.hash order by ap.path asc

--Unmatched character assets
select ap_ancs.*, ap2.* from asset_references ar
inner join asset_paths ap_ancs on ar.source = ap_ancs.hash
inner join asset_paths ap2 on ar.target = ap2.hash
where ap_ancs.path like '%.acs'
and ap2.path not like '%.part'
and ap_ancs.path_matches <> ap2.path_matches
and (ap_ancs.path_matches = 1 or (ap2.path not like '$/Characters/Samus/cooked/%' or ap2.path like '%.ani'))
and ar.game = 'MP1/1.00'
order by ap_ancs.path

--Unmatched model textures
select ap_cmdl.*, ap2.* from asset_references ar
inner join asset_paths ap_cmdl on ar.source = ap_cmdl.hash
inner join asset_paths ap2 on ar.target = ap2.hash
where ap_cmdl.path like '%.cmdl'
and ap_cmdl.path_matches = 1 and ap2.path_matches = 0
and ar.game = 'MP1/1.00'
order by ap_cmdl.path