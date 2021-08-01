# -*- coding: utf-8 -*-
# Copyright (c) 2021, omar jaber and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_to_date, cstr

class RosterDailyReport(Document):
	def autoname(self):
		self.name = self.date + "|" + add_to_date(self.date, days=14)