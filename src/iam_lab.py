"""
Enterprise IAM Architecture Lab

This module simulates a modern enterprise IAM ecosystem demonstrating:
- Identity Governance
- Zero Trust Security
- Identity Federation
- Automated Provisioning
- Access Certification
- RBAC Authorization
"""

from datetime import datetime, timedelta
import hashlib

class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.roles = []
        self.groups = []
        self.last_auth_time = None
        self.mfa_enabled = True
        self.account_status = 'active'
        self.provisioned_resources = []

    def assign_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def assign_group(self, group):
        if group not in self.groups:
            self.groups.append(group)

    def authenticate(self, password_hash):
        # Simulate authentication with MFA check
        if self.account_status == 'active' and self.mfa_enabled:
            self.last_auth_time = datetime.now()
            return True
        return False

    def has_permission(self, permission, resource=None):
        # RBAC Authorization
        for role in self.roles:
            if role.has_permission(permission, resource):
                return True
        # Check groups
        for group in self.groups:
            for role in group.roles:
                if role.has_permission(permission, resource):
                    return True
        return False

    def check_zero_trust(self, context):
        # Zero Trust: continuous verification
        if not self.last_auth_time or (datetime.now() - self.last_auth_time) > timedelta(minutes=30):
            return False
        # Check context (location, device, etc.)
        return context.get('trusted_device', False)

class Role:
    def __init__(self, role_name, description=""):
        self.role_name = role_name
        self.description = description
        self.permissions = []
        self.policies = []

    def add_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def attach_policy(self, policy):
        if policy not in self.policies:
            self.policies.append(policy)

    def has_permission(self, permission, resource=None):
        if permission in self.permissions:
            return True
        for policy in self.policies:
            if policy.evaluate(permission, resource):
                return True
        return False

class Group:
    def __init__(self, group_name):
        self.group_name = group_name
        self.roles = []
        self.users = []

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)

class Policy:
    def __init__(self, policy_name, statements):
        self.policy_name = policy_name
        self.statements = statements  # List of statements

    def evaluate(self, action, resource=None):
        # Simple policy evaluation
        for statement in self.statements:
            if statement['effect'] == 'Allow' and action in statement.get('actions', []):
                if resource and 'resources' in statement:
                    if resource in statement['resources']:
                        return True
                elif not resource:
                    return True
        return False

class IdentityProvider:
    def __init__(self, name):
        self.name = name
        self.federated_users = {}

    def federate_user(self, external_id, user):
        # Identity Federation
        self.federated_users[external_id] = user

    def authenticate_federated(self, external_id, token):
        # Simulate SAML/OIDC authentication
        if external_id in self.federated_users:
            user = self.federated_users[external_id]
            user.last_auth_time = datetime.now()
            return user
        return None

class ProvisioningEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, condition, action):
        self.rules.append({'condition': condition, 'action': action})

    def provision_user(self, user, attributes):
        # Automated Provisioning
        for rule in self.rules:
            if rule['condition'](attributes):
                rule['action'](user, attributes)

class AccessCertifier:
    def __init__(self):
        self.certifications = []

    def schedule_certification(self, user, reviewer):
        # Access Certification
        certification = {
            'user': user,
            'reviewer': reviewer,
            'status': 'pending',
            'due_date': datetime.now() + timedelta(days=30)
        }
        self.certifications.append(certification)

    def certify_access(self, certification_id, approved):
        for cert in self.certifications:
            if cert['id'] == certification_id:
                cert['status'] = 'approved' if approved else 'revoked'

class IAMSystem:
    def __init__(self):
        self.users = {}
        self.roles = {}
        self.groups = {}
        self.policies = {}
        self.idps = {}
        self.provisioning = ProvisioningEngine()
        self.certifier = AccessCertifier()

    def create_user(self, user_id, name, email):
        user = User(user_id, name, email)
        self.users[user_id] = user
        return user

    def create_role(self, role_name, description=""):
        role = Role(role_name, description)
        self.roles[role_name] = role
        return role

    def create_group(self, group_name):
        group = Group(group_name)
        self.groups[group_name] = group
        return group

    def create_policy(self, policy_name, statements):
        policy = Policy(policy_name, statements)
        self.policies[policy_name] = policy
        return policy

    def add_identity_provider(self, name):
        idp = IdentityProvider(name)
        self.idps[name] = idp
        return idp

# Example usage demonstrating enterprise IAM features
if __name__ == "__main__":
    iam = IAMSystem()

    # Create roles with RBAC
    admin_role = iam.create_role("Admin", "Full administrative access")
    admin_role.add_permission("manage_users")
    admin_role.add_permission("manage_roles")

    user_role = iam.create_role("User", "Basic user access")
    user_role.add_permission("read_data")

    # Create policy for fine-grained access
    data_policy = iam.create_policy("DataAccess", [
        {"effect": "Allow", "actions": ["read_data"], "resources": ["database"]}
    ])
    user_role.attach_policy(data_policy)

    # Create groups
    admin_group = iam.create_group("Administrators")
    admin_group.add_role(admin_role)

    # Create users
    admin_user = iam.create_user("admin1", "Admin User", "admin@company.com")
    admin_user.assign_role(admin_role)
    admin_user.assign_group(admin_group)

    regular_user = iam.create_user("user1", "Regular User", "user@company.com")
    regular_user.assign_role(user_role)

    # Identity Federation
    google_idp = iam.add_identity_provider("Google")
    google_idp.federate_user("google_user_123", regular_user)

    # Automated Provisioning
    def provision_based_dept(attributes):
        return attributes.get('department') == 'IT'

    def assign_admin_role(user, attributes):
        user.assign_role(admin_role)

    iam.provisioning.add_rule(provision_based_dept, assign_admin_role)

    # Provision user based on attributes
    iam.provisioning.provision_user(admin_user, {'department': 'IT'})

    # Access Certification
    iam.certifier.schedule_certification(regular_user, admin_user)

    # Demonstrate Zero Trust
    context = {'trusted_device': True, 'location': 'office'}
    print(f"Zero Trust check for {regular_user.name}: {regular_user.check_zero_trust(context)}")

    # Check permissions
    print(f"{admin_user.name} has manage_users permission: {admin_user.has_permission('manage_users')}")
    print(f"{regular_user.name} has read_data permission: {regular_user.has_permission('read_data', 'database')}")

    print("Enterprise IAM simulation complete.")
