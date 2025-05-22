# Automated Member Retention and Communication Implementation

## Overview

This document outlines the implementation approach for automating member retention and communication within the Training Club Fitness Platform. The goal is to create a proactive, data-driven system that engages members, reduces churn, and minimizes manual administrative workload, aligning with the automation-first principle.

## Core Components

### 1. Automation Engine

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class AutomationEngine:
    def __init__(self, db_connection, analytics_engine, communication_service):
        self.db = db_connection
        self.analytics = analytics_engine
        self.communication = communication_service
        self.scheduler = BackgroundScheduler()
        self.workflows = self._load_workflows()
    
    def start(self):
        """Start the automation engine and schedule workflows"""
        # Schedule daily check for triggers
        self.scheduler.add_job(
            self._check_triggers_and_run_workflows,
            'cron',
            hour=4,  # Run at 4 AM
            minute=0
        )
        
        # Schedule immediate trigger checks (e.g., after signup)
        # This would be handled by event listeners in a real system
        
        self.scheduler.start()
        print("Automation Engine started.")
    
    def _load_workflows(self):
        """Load enabled automation workflows from the database"""
        return self.db.get_enabled_automation_workflows()
    
    def reload_workflows(self):
        """Reload workflows, e.g., after admin changes configuration"""
        self.workflows = self._load_workflows()
        print("Automation workflows reloaded.")
    
    def _check_triggers_and_run_workflows(self):
        """Check all triggers and execute corresponding workflows for eligible members"""
        print(f"Running daily automation checks at {datetime.now()}")
        all_members = self.db.get_all_active_members()
        
        for workflow in self.workflows:
            print(f"Checking workflow: {workflow['name']}")
            trigger_type = workflow['trigger']['type']
            trigger_params = workflow['trigger']['params']
            
            eligible_members = []
            
            if trigger_type == 'low_engagement':
                eligible_members = self._check_low_engagement_trigger(all_members, trigger_params)
            elif trigger_type == 'high_retention_risk':
                eligible_members = self._check_retention_risk_trigger(all_members, trigger_params)
            elif trigger_type == 'membership_expiry_upcoming':
                eligible_members = self._check_membership_expiry_trigger(all_members, trigger_params)
            elif trigger_type == 'milestone_achieved':
                eligible_members = self._check_milestone_trigger(all_members, trigger_params)
            elif trigger_type == 'new_member_welcome':
                # This would typically be event-driven, but can have a fallback check
                eligible_members = self._check_new_member_trigger(all_members, trigger_params)
            elif trigger_type == 'birthday':
                eligible_members = self._check_birthday_trigger(all_members, trigger_params)
            # Add more trigger types as needed
            
            if eligible_members:
                print(f"  Found {len(eligible_members)} members for workflow '{workflow['name']}'")
                for member_id in eligible_members:
                    # Check cooldown period for this member and workflow
                    if not self._is_on_cooldown(member_id, workflow['id']):
                        self._execute_workflow(member_id, workflow)
                    else:
                        print(f"  Member {member_id} is on cooldown for workflow {workflow['id']}")
            else:
                print(f"  No members eligible for workflow '{workflow['name']}'")

    def _execute_workflow(self, member_id, workflow):
        """Execute the steps defined in a workflow for a specific member"""
        print(f"  Executing workflow '{workflow['name']}' for member {member_id}")
        member_info = self.db.get_member_details(member_id)
        if not member_info:
            print(f"  Error: Member {member_id} not found.")
            return

        for step in workflow['steps']:
            action_type = step['action']['type']
            action_params = step['action']['params']
            
            try:
                if action_type == 'send_email':
                    self.communication.send_automated_email(
                        recipient_email=member_info['email'],
                        template_id=action_params['template_id'],
                        context=self._prepare_context(member_info, workflow, step)
                    )
                elif action_type == 'send_in_app_notification':
                    self.communication.send_in_app_notification(
                        member_id=member_id,
                        template_id=action_params['template_id'],
                        context=self._prepare_context(member_info, workflow, step)
                    )
                elif action_type == 'add_tag':
                    self.db.add_member_tag(member_id, action_params['tag'])
                elif action_type == 'assign_task_to_staff':
                    self._assign_staff_task(member_id, action_params)
                elif action_type == 'offer_discount':
                    self._apply_discount_offer(member_id, action_params)
                elif action_type == 'grant_credits':
                    self.db.grant_credits(member_id, action_params['amount'], f"Automated workflow: {workflow['name']}")
                # Add more action types
                
                # Log successful execution
                self.db.log_automation_action(member_id, workflow['id'], step['id'], success=True)
                
                # Set cooldown period
                self._set_cooldown(member_id, workflow['id'], workflow.get('cooldown_period_days', 7))

            except Exception as e:
                print(f"  Error executing step {step['id']} for member {member_id}: {str(e)}")
                self.db.log_automation_action(member_id, workflow['id'], step['id'], success=False, error_message=str(e))

    def _prepare_context(self, member_info, workflow, step):
        """Prepare context data for communication templates"""
        # Base context with member info
        context = {
            'member_first_name': member_info.get('first_name'),
            'member_last_name': member_info.get('last_name'),
            'member_email': member_info.get('email'),
            'membership_level': member_info.get('membership_level'),
            'join_date': member_info.get('join_date'),
            # Add more standard member fields
        }
        # Add workflow-specific context if needed
        context.update(workflow.get('context', {}))
        # Add step-specific context if needed
        context.update(step.get('context', {}))
        return context

    # --- Trigger Check Methods ---
    def _check_low_engagement_trigger(self, members, params):
        """Identify members with low engagement based on parameters"""
        threshold_days = params.get('inactive_days', 30)
        min_activity_level = params.get('min_activity_level', 'low') # e.g., 'low', 'medium', 'high'
        
        eligible_members = []
        for member in members:
            last_activity_date = self.db.get_member_last_activity_date(member['id'])
            if last_activity_date and (datetime.now().date() - last_activity_date).days >= threshold_days:
                # Further check activity level if needed
                eligible_members.append(member['id'])
        return eligible_members

    def _check_retention_risk_trigger(self, members, params):
        """Identify members with high retention risk"""
        risk_threshold = params.get('risk_score_threshold', 0.7)
        member_ids = [m['id'] for m in members]
        risk_scores = self.analytics.predict_retention_risk_batch(member_ids) # Assumes batch prediction method exists
        
        eligible_members = []
        for member_risk in risk_scores:
            if member_risk['risk_score'] >= risk_threshold:
                eligible_members.append(member_risk['member_id'])
        return eligible_members

    def _check_membership_expiry_trigger(self, members, params):
        """Identify members whose membership is expiring soon"""
        days_before_expiry = params.get('days_before', 14)
        target_date = datetime.now().date() + timedelta(days=days_before_expiry)
        
        eligible_members = []
        for member in members:
            expiry_date = self.db.get_member_membership_expiry(member['id'])
            if expiry_date and expiry_date == target_date:
                eligible_members.append(member['id'])
        return eligible_members

    def _check_milestone_trigger(self, members, params):
        """Identify members who achieved a specific milestone"""
        milestone_type = params.get('type') # e.g., 'classes_attended', 'anniversary'
        milestone_value = params.get('value')
        
        eligible_members = []
        for member in members:
            achieved = self.db.check_member_milestone(member['id'], milestone_type, milestone_value)
            if achieved:
                eligible_members.append(member['id'])
        return eligible_members
        
    def _check_new_member_trigger(self, members, params):
        """Identify new members within a certain timeframe"""
        days_since_join = params.get('days_since_join', 1)
        target_join_date = datetime.now().date() - timedelta(days=days_since_join)
        
        eligible_members = []
        for member in members:
             join_date = self.db.get_member_join_date(member['id'])
             if join_date and join_date == target_join_date:
                 eligible_members.append(member['id'])
        return eligible_members
        
    def _check_birthday_trigger(self, members, params):
        """Identify members whose birthday is today"""
        today_month_day = datetime.now().strftime('%m-%d')
        eligible_members = []
        for member in members:
            birth_date = self.db.get_member_birth_date(member['id'])
            if birth_date and birth_date.strftime('%m-%d') == today_month_day:
                eligible_members.append(member['id'])
        return eligible_members

    # --- Action Helper Methods ---
    def _assign_staff_task(self, member_id, params):
        """Assign a task to a staff member related to a member"""
        task_description = params.get('description', f"Follow up with member {member_id}")
        assignee_rule = params.get('assignee_rule', 'member_primary_trainer') # or 'specific_staff_id', 'round_robin'
        due_date_offset = params.get('due_date_offset_days', 3)
        
        # Determine assignee
        assignee_id = None
        if assignee_rule == 'member_primary_trainer':
            assignee_id = self.db.get_member_primary_trainer(member_id)
        elif assignee_rule == 'specific_staff_id':
            assignee_id = params.get('staff_id')
        # Add logic for round_robin etc.
        
        if assignee_id:
            due_date = datetime.now().date() + timedelta(days=due_date_offset)
            self.db.create_staff_task(assignee_id, member_id, task_description, due_date)
            print(f"  Assigned task for member {member_id} to staff {assignee_id}")
        else:
            print(f"  Could not determine assignee for task related to member {member_id}")
            
    def _apply_discount_offer(self, member_id, params):
        """Apply a discount offer to a member's account"""
        offer_code = params.get('offer_code')
        duration_days = params.get('duration_days', 30)
        
        if offer_code:
            expiry_date = datetime.now().date() + timedelta(days=duration_days)
            self.db.apply_member_discount(member_id, offer_code, expiry_date)
            print(f"  Applied discount offer {offer_code} to member {member_id}")
        else:
            print(f"  Missing offer_code for discount action for member {member_id}")
            
    # --- Cooldown Management ---
    def _is_on_cooldown(self, member_id, workflow_id):
        """Check if the member is currently on cooldown for this workflow"""
        last_run_time = self.db.get_last_workflow_run_time(member_id, workflow_id)
        if not last_run_time:
            return False
            
        workflow = next((w for w in self.workflows if w['id'] == workflow_id), None)
        if not workflow:
            return False # Should not happen
            
        cooldown_days = workflow.get('cooldown_period_days', 7)
        cooldown_delta = timedelta(days=cooldown_days)
        
        return datetime.now() < (last_run_time + cooldown_delta)
        
    def _set_cooldown(self, member_id, workflow_id, cooldown_days):
        """Record the execution time to enforce cooldown"""
        # This is implicitly handled by logging the action time in db.log_automation_action
        # The _is_on_cooldown method reads this log.
        pass 
```

### 2. Communication Service

```python
class CommunicationService:
    def __init__(self, db_connection, email_provider, notification_system):
        self.db = db_connection
        self.email_provider = email_provider # e.g., SendGrid, Mailgun
        self.notification_system = notification_system # Handles in-app notifications
    
    def send_automated_email(self, recipient_email, template_id, context):
        """Send an email using a predefined template and context"""
        template = self.db.get_communication_template(template_id, 'email')
        if not template:
            print(f"Error: Email template {template_id} not found.")
            return
        
        subject = self._render_template(template['subject'], context)
        body = self._render_template(template['body_html'], context)
        text_body = self._render_template(template.get('body_text', ''), context)
        
        try:
            self.email_provider.send(
                to=recipient_email,
                subject=subject,
                html_body=body,
                text_body=text_body,
                from_address=template.get('from_address', 'noreply@trainingclub.ch'),
                from_name=template.get('from_name', 'Training Club')
            )
            print(f"  Sent email using template {template_id} to {recipient_email}")
            self._log_communication('email', template_id, recipient_email, success=True)
        except Exception as e:
            print(f"  Error sending email to {recipient_email}: {str(e)}")
            self._log_communication('email', template_id, recipient_email, success=False, error_message=str(e))

    def send_in_app_notification(self, member_id, template_id, context):
        """Send an in-app notification"""
        template = self.db.get_communication_template(template_id, 'in_app')
        if not template:
            print(f"Error: In-app notification template {template_id} not found.")
            return
        
        title = self._render_template(template.get('title', 'Notification'), context)
        message = self._render_template(template['body_text'], context)
        action_url = self._render_template(template.get('action_url', ''), context)
        icon = template.get('icon', 'info')
        
        try:
            self.notification_system.send(
                member_id=member_id,
                title=title,
                message=message,
                action_url=action_url,
                icon=icon
            )
            print(f"  Sent in-app notification using template {template_id} to member {member_id}")
            self._log_communication('in_app', template_id, f"member_{member_id}", success=True)
        except Exception as e:
            print(f"  Error sending in-app notification to member {member_id}: {str(e)}")
            self._log_communication('in_app', template_id, f"member_{member_id}", success=False, error_message=str(e))

    def _render_template(self, template_string, context):
        """Render a template string with the given context (e.g., using Jinja2)"""
        # Simple substitution for example, replace with Jinja2 or similar
        rendered = template_string
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}" # e.g., {{member_first_name}}
            rendered = rendered.replace(placeholder, str(value) if value is not None else '')
        return rendered
        
    def _log_communication(self, channel, template_id, recipient_identifier, success, error_message=None):
        """Log communication attempt and outcome"""
        self.db.log_communication_event(
            channel=channel,
            template_id=template_id,
            recipient=recipient_identifier,
            status='sent' if success else 'failed',
            error_message=error_message
        )
```

## Frontend Implementation

### 1. Admin Workflow Configuration UI

- **Workflow List**: Display all available automation workflows (enabled and disabled).
- **Workflow Editor**: Allow admins to:
    - Create new workflows.
    - Enable/disable existing workflows.
    - Configure triggers (type, parameters like days inactive, risk score threshold).
    - Define steps (action type, parameters like template ID, tag name, staff assignment rules).
    - Set cooldown periods.
    - Define context variables.
- **Template Management**: Interface to create and edit email and in-app notification templates with placeholders.
- **Automation Logs**: View logs of workflow executions, successes, and failures.

### 2. Member Notification Center

- Display in-app notifications received by the member.
- Allow members to mark notifications as read or dismiss them.
- Link notifications to relevant sections of the app (e.g., a discount offer notification links to the membership page).

## Database Schema Updates

```sql
-- Automation Workflows
CREATE TABLE automation_workflows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    trigger JSON NOT NULL, -- { "type": "low_engagement", "params": { "inactive_days": 30 } }
    steps JSON NOT NULL,   -- [ { "id": 1, "action": { "type": "send_email", "params": { "template_id": 123 } }, "context": {} } ]
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    cooldown_period_days INT NOT NULL DEFAULT 7, -- Cooldown in days
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Communication Templates
CREATE TABLE communication_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    channel ENUM('email', 'in_app', 'sms') NOT NULL,
    subject VARCHAR(255), -- For email
    title VARCHAR(100),   -- For in-app
    body_html LONGTEXT,   -- For email
    body_text LONGTEXT NOT NULL, -- For email text version, in-app message, sms
    from_address VARCHAR(255), -- For email
    from_name VARCHAR(100),    -- For email
    action_url VARCHAR(512),   -- For in-app
    icon VARCHAR(50),          -- For in-app
    placeholders JSON, -- List of available placeholders like ["member_first_name", "offer_code"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Automation Logs
CREATE TABLE automation_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    workflow_id INT NOT NULL,
    step_id INT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES automation_workflows(id) ON DELETE CASCADE
);

-- Communication Logs
CREATE TABLE communication_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    channel ENUM('email', 'in_app', 'sms') NOT NULL,
    template_id INT,
    recipient VARCHAR(255) NOT NULL, -- Email address or member_id identifier
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sent', 'failed', 'delivered', 'opened', 'clicked') NOT NULL,
    error_message TEXT,
    event_data JSON, -- For tracking opens, clicks etc.
    FOREIGN KEY (template_id) REFERENCES communication_templates(id) ON DELETE SET NULL
);

-- Member Tags
CREATE TABLE member_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    tag VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member_tag (member_id, tag)
);

-- Staff Tasks
CREATE TABLE staff_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignee_id INT NOT NULL, -- Staff user ID
    related_member_id INT,
    description TEXT NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (related_member_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Member Offers/Discounts
CREATE TABLE member_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    offer_code VARCHAR(50) NOT NULL,
    description TEXT,
    expiry_date DATE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL,
    FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Integration Points

- **Analytics Engine**: The Automation Engine relies heavily on the `AdvancedAnalyticsEngine` to get data for triggers (e.g., retention risk scores, activity levels).
- **Member Data**: Needs access to comprehensive member data including activity logs, membership status, join dates, birthdays, etc.
- **Admin UI**: Requires new sections for configuring workflows, managing templates, and viewing logs.
- **Member Portal**: Needs a notification center to display in-app messages.
- **External Services**: Requires integration with an email provider and potentially an SMS provider.

## Next Steps

1. Implement the `AutomationEngine` backend logic.
2. Develop the `CommunicationService` and integrate with chosen providers.
3. Update the database schema with automation-related tables.
4. Implement the Admin UI for workflow and template management.
5. Implement the Member Notification Center in the frontend.
6. Define initial set of default workflows and templates.
7. Test the end-to-end automation flows thoroughly.
