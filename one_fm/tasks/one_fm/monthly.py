import frappe, calendar
from frappe.utils import (
    nowdate, getdate, add_days
)
from frappe import enqueue
from one_fm.api.tasks import assign_am_shift, assign_pm_shift

def execute():
    enqueue('one_fm.tasks.one_fm.monthly.employee_schedule_monthly')




def employee_schedule_monthly():
    """
        This method auto schedule employees every first day of the month.
    """
    settings = frappe.get_doc('Employee Schedule Setting')
    if settings.active:
        exempt_projects = [row.project for row in settings.exempt_projects]
        projects = frappe.db.get_list(
            'Project',
            filters={'name':['NOT IN', exempt_projects], 'exempt_auto_employee_schedule':0,
                'project_type':'External'}
            )
        # get dates
        today = getdate()
        last_month_date = add_days(today, -1)
        last_day_of_current_month = calendar.monthrange(today.year, today.month)[1]
        for p in projects:
            employee_schedule = frappe.db.get_list("Employee Schedule",
                filters={'date':str(last_month_date), 'project':p.name},
                fields=['name', 'employee'])
            for row in employee_schedule:
                if frappe.db.exists("Employee", {'status':'Active', 'name':row.employee}):
                    for i in range(1, last_day_of_current_month):
                        try:
                            es = frappe.get_doc("Employee Schedule", row.name)
                            es.creation = ''
                            es.modified_by = ''
                            es.owner = ''
                            es.roster_type = 'Basic'
                            es.employee_availability = 'Working'
                            es.date = f'{today.year}-{today.month}-{i}'
                            es.insert()
                        except Exception as e:
                            pass
            frappe.db.commit()

        # RUN SHIFT ASSIGNMENTS
        assign_am_shift()
