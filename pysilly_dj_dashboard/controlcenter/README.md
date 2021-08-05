Fork of: https://github.com/byashimov/django-controlcenter

Added:

- Remove settings variable to register dashbaords, added a registry in `registry`

```
@DashboardRegistry.register(dashbaord_pk: str, set_as_home: bool = False)
```

Uses:
```
@DashboardRegistry.register('campaign-overview')
class CampaignOverviewDashboard(CampaignDashboardBase):
    widgets = (
        (TrackOverTimeWidget, ),
        (
            CampaignOverviewStaticList,
            CampaignTagItemList
        )
    )

@DashboardRegistry.register('organization-overview', set_as_home=True)
class OrganizationOverviewDashboard(Dashboard):
    widgets = (
        CampaignItemList,
    )
```

- Added a master tempalte to widgets

- Remove `Group`, use tuples/lists to group widgets. 

- Auto size based on the 12 rule of bootrap

Uses:
```
@DashboardRegistry.register('campaign-overview')
class CampaignOverviewDashboard(CampaignDashboardBase):
    widgets = (
        (TrackOverTimeWidget, ),  # Group 1 - has one element size 12.
        (  # Group 2 - has two elements, each with a size of 6.
            CampaignOverviewStaticList, 
            CampaignTagItemList
        )
    )
```
