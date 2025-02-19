# /// script
# dependencies = [
#   "sling",
#   "kestra",
# ]
# ///

from sling import Replication

config = {
    "source": "MSSQL",
    "target": "PSQL",
    "defaults": {"mode": "incremental", "target_options": {"column_casing": "snake"}},
    "streams": {
        "category": {
            "mode": "incremental",
            "primary_key": ["id"],
            "object": "public.projects_category",
            "sql": """
                select
                    KategoriId as id
                    , Kategori as text
                from NINA_prosjekt_oversikt
                group by KategoriId, Kategori
            """,
        },
        "section": {
            "mode": "incremental",
            "primary_key": ["id"],
            "object": "public.projects_section",
            "sql": """
                select
                    dim_value as id
                    , description as text
                from NINA_avdelinger
                where description <> 'Eliminering og fordeling'
            """,
        },
        "projects": {
            "mode": "incremental",
            "primary_key": ["number"],
            "object": "public.projects_project",
            "sql": """
                select
                    Prosjektnr as number
                    , Prosjektnavn as name
                    , Startdato as start_date
                    , Sluttdato as end_date
                    , Status as status
                    , Oppdragsgiver as customer
                    , AvdelingId as section_id
                    , KategoriId as category_id
                    , TotalRamme as budget
                from NINA_prosjekt_oversikt as npo
                join NINA_projects_budget as npb
                    on npo.Prosjektnr = npb.Prosjekt
            """,
        },
        "membership": {
            "mode": "incremental",
            "primary_key": ["project_id", "user_id"],
            "object": "public.projects_projectmembership",
            "sql": """
                select
                    prosjektID as project_id
                    , ansattID as user_id
                    , case
                        when ansattID = ansvarlig then 'owner'
                        else 'member'
                    end as role
                from dbo.NINA_Prosjekt_Ressurser
            """,
        },
    },
    "env": {"SLING_LOGGING": "JSON"},
}

result = Replication(**config).run()
