# -*- coding: utf-8 -*-

import logging
from datetime import timedelta, datetime, date

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class TaskBA(models.Model):
    _inherit = ['project.task']
    
    checklist = fields.Many2one('ba_task_checklist.checklist', string='Checklist')
    checklist_items = fields.One2many('ba_task_checklist.task_checklist_item', 'task', string='Items')
    checklist_progress = fields.Float(string='Checklist Progress', compute='_compute_total')
    
    @api.depends('checklist_items')
    def _compute_total(self):
        for record in self:
            sum_done = 0
            for item in record.checklist_items:
                if item.done or item.cancel:
                    sum_done += 1
            if sum_done:    
                record.checklist_progress = (sum_done / len(record.checklist_items)) * 100
            else:
                record.checklist_progress = 0.1
                
    @api.onchange('checklist')            
    def _onchange_checklist(self):
        for item in self.checklist_items:
            self.checklist_items = [(2, item.id, _)]
        i = []    
        for item in self.checklist.items:
            i.append((0, 0, {'sequence': item.sequence,
                             'name': item.name,
                             'description': item.description,
                     }))
        self.checklist_items = i
        
class ChecklistBA(models.Model):
    _name = 'ba_task_checklist.checklist'
    
    name = fields.Char(string='Name')
    items = fields.One2many('ba_task_checklist.checklist_item', 'checklist', string='Items')
    description = fields.Char(string='Description')
        
    
class ChecklistItem(models.Model):
    _name = 'ba_task_checklist.checklist_item'

    checklist = fields.Many2one('ba_task_checklist.checklist')
    
    sequence = fields.Integer(default=1)
    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    
        
class TaskChecklistItem(models.Model):
    _name = 'ba_task_checklist.task_checklist_item'

    task = fields.Many2one('project.task')
    
    sequence = fields.Integer(default=1)
    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    done = fields.Boolean(string='Done')
    cancel = fields.Boolean(string='Cancel')
    result = fields.Selection([('complete','Complete'),('cancel','Cancel')], string='Result')
    
    def click_done(self):
        self.done = True
        self.cancel = False
        self.result = 'complete'
        
    def click_cancel(self):
        self.done = False         
        self.cancel = True
        self.result = 'cancel'