"""Admin service for shared business logic"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json

from src.plugins.database import db


class AdminService:
    """Service handling admin operations"""
    
    async def log_admin_action(
        self,
        admin_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log an admin action"""
        try:
            log_entry = await db.client.adminlog.create(
                data={
                    'admin_id': admin_id,
                    'action_type': action_type,
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'old_values': json.dumps(old_values) if old_values else None,
                    'new_values': json.dumps(new_values) if new_values else None,
                    'reason': reason,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            )
            return log_entry
        except Exception as e:
            raise Exception(f"Error logging admin action: {str(e)}")
    
    async def get_admin_logs(
        self,
        admin_id: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get paginated admin logs"""
        try:
            where = {}
            if admin_id:
                where['admin_id'] = admin_id
            if action_type:
                where['action_type'] = action_type
            if entity_type:
                where['entity_type'] = entity_type
            
            total = await db.client.adminlog.count(where=where)
            
            logs = await db.client.adminlog.find_many(
                where=where,
                skip=(page - 1) * per_page,
                take=per_page,
                order_by=[{'created_at': 'desc'}],
                include={'admin': True}
            )
            
            return {
                'logs': logs,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            raise Exception(f"Error fetching admin logs: {str(e)}")
    
    async def change_user_role(
        self,
        admin_id: str,
        user_id: str,
        new_role: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Change user role (admin only)"""
        try:
            # Get old user data
            user = await db.client.user.find_unique(where={'id': user_id})
            if not user:
                raise ValueError("User not found")
            
            old_role = user.role
            
            # Update user role
            updated_user = await db.client.user.update(
                where={'id': user_id},
                data={'role': new_role}
            )
            
            # Log the action
            await self.log_admin_action(
                admin_id=admin_id,
                action_type='ROLE_CHANGE',
                entity_type='User',
                entity_id=user_id,
                old_values={'role': old_role},
                new_values={'role': new_role},
                reason=reason
            )
            
            return {
                'success': True,
                'user_id': user_id,
                'old_role': old_role,
                'new_role': new_role
            }
        except Exception as e:
            raise Exception(f"Error changing user role: {str(e)}")
    
    async def deactivate_user(
        self,
        admin_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deactivate a user"""
        try:
            user = await db.client.user.find_unique(where={'id': user_id})
            if not user:
                raise ValueError("User not found")
            
            updated_user = await db.client.user.update(
                where={'id': user_id},
                data={'is_active': False}
            )
            
            await self.log_admin_action(
                admin_id=admin_id,
                action_type='DEACTIVATE',
                entity_type='User',
                entity_id=user_id,
                old_values={'is_active': True},
                new_values={'is_active': False},
                reason=reason
            )
            
            return {'success': True, 'user_id': user_id, 'is_active': False}
        except Exception as e:
            raise Exception(f"Error deactivating user: {str(e)}")
    
    async def activate_user(
        self,
        admin_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Activate a user"""
        try:
            user = await db.client.user.find_unique(where={'id': user_id})
            if not user:
                raise ValueError("User not found")
            
            updated_user = await db.client.user.update(
                where={'id': user_id},
                data={'is_active': True}
            )
            
            await self.log_admin_action(
                admin_id=admin_id,
                action_type='ACTIVATE',
                entity_type='User',
                entity_id=user_id,
                old_values={'is_active': False},
                new_values={'is_active': True},
                reason=reason
            )
            
            return {'success': True, 'user_id': user_id, 'is_active': True}
        except Exception as e:
            raise Exception(f"Error activating user: {str(e)}")
    
    async def adjust_inventory(
        self,
        admin_id: str,
        inventory_id: str,
        change_type: str,
        quantity: int,
        reason: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adjust product inventory"""
        try:
            inventory = await db.client.productinventory.find_unique(
                where={'id': inventory_id}
            )
            if not inventory:
                raise ValueError("Inventory not found")
            
            old_level = inventory.stock_level
            new_level = old_level
            
            if change_type == 'ADD':
                new_level += quantity
            elif change_type == 'REMOVE':
                new_level -= quantity
                if new_level < 0:
                    raise ValueError("Cannot remove more stock than available")
            elif change_type == 'ADJUST':
                new_level = quantity
            else:
                raise ValueError("Invalid change type")
            
            # Update inventory
            updated_inventory = await db.client.productinventory.update(
                where={'id': inventory_id},
                data={'stock_level': new_level}
            )
            
            # Log inventory change
            await db.client.inventorylog.create(
                data={
                    'inventory_id': inventory_id,
                    'change_type': change_type,
                    'quantity': quantity if change_type == 'ADJUST' else (quantity if change_type == 'ADD' else -quantity),
                    'reason': reason,
                    'note': note,
                    'created_by': admin_id
                }
            )
            
            return {
                'success': True,
                'inventory_id': inventory_id,
                'old_stock': old_level,
                'new_stock': new_level,
                'change': quantity if change_type in ['ADD', 'REMOVE'] else None
            }
        except Exception as e:
            raise Exception(f"Error adjusting inventory: {str(e)}")
    
    async def get_low_stock_products(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get products with low stock"""
        try:
            inventories = await db.client.productinventory.find_many(
                include={'product': True}
            )
            
            low_stock = [
                inv for inv in inventories
                if inv.stock_level <= inv.low_stock_threshold
            ]
            
            # Paginate
            total = len(low_stock)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated = low_stock[start_idx:end_idx]
            
            return {
                'inventories': paginated,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            raise Exception(f"Error getting low stock products: {str(e)}")


# Singleton instance
admin_service = AdminService()
