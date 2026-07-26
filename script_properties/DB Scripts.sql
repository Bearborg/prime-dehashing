select * from property_names
where type = 'AudioPlaybackParms'
order by name_matches desc

select * from property_names where name like '%Data' and name_matches = 0

--Per-game stats
with grouped_usages as (select hash, source_game from property_usages group by hash, source_game)
select source_game as game, sum(pn.name_matches) as matched, count(pn.hash) as total, round((100.0 * sum(pn.name_matches)) / count(pn.hash), 2) as pct from grouped_usages pu
inner join property_names pn on pn.hash = pu.hash
group by pu.source_game

--Property types without confirmed matches
select pn.type, count(*) as instances from property_names pn
inner join property_usages pu on pn.hash = pu.hash
where pu.source_game <> 'DKCR'
group by pn.type
having sum(name_matches) = 0

--Property types with unmatched properties
select type, count(*) - sum(name_matches) as unmatched, sum(name_matches) as matched from property_names
group by type
having min(name_matches) = 0 and sum(name_matches) > 0
order by count(*) - sum(name_matches) desc, sum(name_matches) desc

--Templates with unmatched properties, by type
select pn.type, pu.source_template, pu.source_game, count(*) - sum(pn.name_matches) as unmatched from property_names pn
inner join property_usages pu on pn.hash = pu.hash
where pn.type = 'float'
group by pu.source_template, pu.source_game
having min(pn.name_matches) = 0
order by count(*) - sum(pn.name_matches) desc

--Unmatched default enums
with numbered_enums as (SELECT ROW_NUMBER() OVER () AS row_num, * FROM enum_names)
select min(row_num), hash, name from numbered_enums group by game, source having name_matches = 0

--Sorted unmatched enums
select hash, max(name) as name, IIF( MAX(IIF(game = 'MP3', 1, 0)), 'MP3', max(game)) as game, max(source) as source, max(name_matches) as name_matches
from enum_names where name_matches = 0 group by hash order by MAX(IIF(game = 'MP3', 1, 0)) desc, source, game, name

--Unmatched enums by source
select hash, max(name) as name, source, game, max(name_matches) as name_matches
from enum_names where name_matches = 0 and source = 'Script/SpecialFunction.xml'
group by hash order by source, game, name

--Enum values shared across sources
select hash, group_concat(source, ',') from enum_names
group by hash
having count(distinct source) > 1

--Enum stats
with distinct_enums as (select hash, name_matches from enum_names group by hash)
select name_matches, count(*) from distinct_enums group by name_matches

--All properties of source
select * from property_names pn
INNER JOIN property_usages pu on pn.hash = pu.hash
where
pu.source_template like '%Structs/UnknownStruct10.xml%'
and pu.source_game = 'MP2'
order by pu.id

--All sibling properties
with vals as (
	select 
	'0x37ded7f2' as goal,
	'' as goal_game
),
selected_template as (
	select * from vals, property_usages
	where hash = vals.goal collate nocase and
	IIF(vals.goal_game = '', 1, vals.goal_game = source_game)
	order by id
)
select IIF(pn.hash = vals.goal collate nocase, ' -->', '') as ' ', pn.*, pu.id, pu.source_template, pu.source_game from vals, selected_template, property_names pn
INNER JOIN property_usages pu on pn.hash = pu.hash and selected_template.source_game = pu.source_game and selected_template.source_template = pu.source_template
order by pu.id

--Unnatched properties by source
select *, group_concat(source_game, ',') from property_names pn
INNER JOIN property_usages pu on pn.hash = pu.hash
where
pu.source_template like '%/GuiChar%'
and pu.source_game = 'DKCR'
and pn.name_matches = 0
group by pu.hash
order by min(id)

--Miguel's wishlist
select *, group_concat(source_game, ',') from property_names pn
INNER JOIN property_usages pu on pn.hash = pu.hash
where
pu.source_template IN ('Script/Actor.xml','Script/Platform.xml', 'Structs/ActorParameters.xml')
and pu.source_game like 'MP%'
and pn.name_matches = 0
group by pu.hash
order by min(id)