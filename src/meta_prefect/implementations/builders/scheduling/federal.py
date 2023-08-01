"""Federal holiday schedule updater."""
import datetime
from typing import cast, List, Optional, Union

from holidays.countries.united_states import UnitedStates
from prefect.client.schemas.schedules import (
    CronSchedule as ClientCronSchedule,
    IntervalSchedule as ClientIntervalSchedule,
    RRuleSchedule as ClientRRuleSchedule,
)
from prefect.server.schemas.schedules import (
    CronSchedule as ServerCronSchedule,
    IntervalSchedule as ServerIntervalSchedule,
    RRuleSchedule as ServerRRuleSchedule,
)
from prefect.utilities.asyncutils import sync_compatible
from pydantic import BaseModel

from meta_prefect.interface.builder import DeployableFlowBuilderInterface
from meta_prefect.interface.deployment import Deployment
from meta_prefect.interface.flow import DeployableFlow

RRuleSchedule = Union[ClientRRuleSchedule, ServerRRuleSchedule]


class federal_holiday_schedule_updater(BaseModel, DeployableFlowBuilderInterface):
    """Federal holiday schedule updater."""

    schedule: Optional[ClientRRuleSchedule] = None
    horizon_years: int = 1

    def _get_holidays(self) -> List[datetime.date]:
        # Get a list of holidays for the current year
        return cast(
            List[datetime.date],
            list(
                UnitedStates(  # type: ignore [no-untyped-call]
                    years=[
                        datetime.date.today().year + i
                        for i in range(self.horizon_years + 1)
                    ]
                ).keys()
            ),
        )

    def _update_rrule_schedule(
        self, schedule: ClientRRuleSchedule
    ) -> ClientRRuleSchedule:
        """Update the rrule schedule."""
        holidays = self._get_holidays()
        holiday_str = ",".join(
            [holiday.strftime("%Y%m%dT%H%M%S") for holiday in holidays]
        )
        if "EXDATE" in schedule.rrule:
            new_rrule = schedule.rrule + f",{holiday_str}"
        else:
            new_rrule = schedule.rrule + f"\nEXDATE:{holiday_str}"

        if len(new_rrule) > 6500:
            raise ValueError(
                "The updated schedule exceeds the 6500 character limit. "
                "Please reduce the horizon_years."
            )
        schedule.rrule = new_rrule
        return schedule

    @sync_compatible
    async def update_deployment(
        self, flow: DeployableFlow, deployment: Deployment
    ) -> Deployment:
        """Update the deployment."""
        if self.schedule:
            deployment.schedule = self.schedule

        if deployment.schedule:
            if isinstance(
                deployment.schedule,
                (
                    ClientIntervalSchedule,
                    ServerIntervalSchedule,
                    ClientCronSchedule,
                    ServerCronSchedule,
                ),
            ):
                raise NotImplementedError(
                    "IntervalSchedule and CronSchedule are not supported."
                )
            elif isinstance(
                deployment.schedule, (ClientRRuleSchedule, ServerRRuleSchedule)
            ):
                deployment.schedule = self._update_rrule_schedule(deployment.schedule)
        return deployment
