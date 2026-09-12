--Unmatched prototype assets
select * from asset_paths ap
inner join asset_usages au on ap.hash = au.hash
where au.game = 'MP3P'
and ap.path_matches = 0
group by ap.hash
order by au.type, au.pak, ap.path

--Unmatched area names
select * from asset_paths
where path like '$/strings/metroid3/area_names%'
and path_matches = 0
order by path

--Per-game stats
with grouped_usages as (select hash, game from asset_usages group by hash, game)
select
	game as game,
	sum(ap.path_matches) as matched,
	count(ap.hash) - sum(ap.path_matches) as remaining,
	count(ap.hash) as total,
	round((100.0 * sum(ap.path_matches)) / count(ap.hash), 2) as pct
	from grouped_usages au
inner join asset_paths ap on ap.hash = au.hash
group by au.game

-- Display match stats
with const as (select 'MP3/NTSC' as game, null as pak),
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