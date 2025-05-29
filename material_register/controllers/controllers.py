# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
import base64
import werkzeug.wrappers
import logging
from functools import wraps
from datetime import datetime
from .auth import authenticate_api, invalid_response, valid_response

_logger = logging.getLogger(__name__)


def serialize_date(dt):
    """Convert datetime to string format"""
    return dt.isoformat() if dt else None


def serialize_object(obj):
    """Prepare object for JSON serialization"""
    if isinstance(obj, datetime):
        return serialize_date(obj)
    return str(obj)


class MaterialRegisterAPI(http.Controller):
    """
    RESTful API for Material Register
    Provides CRUD operations for managing materials
    """
    
    @http.route('/api/v1/materials', type='json', auth='none', methods=['GET'], csrf=False)
    @authenticate_api
    def get_materials(self, **kwargs):
        """
        Get all materials with optional filtering
        """
        _logger.info("Fetching materials with parameters: %s", kwargs)
        try:
            # Parse pagination parameters
            limit = int(kwargs.get('limit', 0))
            offset = int(kwargs.get('offset', 0))
            order = kwargs.get('order', 'id desc')
            
            # Build filter domain
            domain = []
            
            # Add filters based on request parameters
            if kwargs.get('material_code'):
                domain.append(('material_code', 'ilike', kwargs.get('material_code')))
                
            if kwargs.get('name'):
                domain.append(('name', 'ilike', kwargs.get('name')))
                
            if kwargs.get('material_type'):
                domain.append(('material_type', '=', kwargs.get('material_type')))
            
            # Get total count for pagination info
            total_count = request.env['material.register'].search_count(domain)
            
            # Fetch materials with pagination
            materials = request.env['material.register'].search(domain, limit=limit, offset=offset, order=order)
            
            # Prepare response data
            material_list = []
            for material in materials:
                material_list.append({
                    'id': material.id,
                    'material_code': material.material_code,
                    'name': material.name,
                    'material_type': material.material_type,
                    'material_buy_price': float(material.material_buy_price),
                    'currency': {
                        'id': material.currency_id.id,
                        'name': material.currency_id.name,
                        'symbol': material.currency_id.symbol
                    },
                    'partner': {
                        'id': material.partner_id.id,
                        'name': material.partner_id.name
                    },
                    'create_date': serialize_date(material.create_date),
                    'write_date': serialize_date(material.write_date),
                })
            
            # Prepare metadata for pagination
            meta = {
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': (offset + len(material_list)) < total_count
            }
            
            return valid_response(
                data=material_list,
                message="Materials retrieved successfully",
                meta=meta
            )
        except Exception as e:
            _logger.exception("Error fetching materials")
            return invalid_response(
                message="Failed to retrieve materials",
                code="MATERIALS_FETCH_ERROR",
                status=500
            )
    
    @http.route('/api/v1/materials/<int:material_id>', type='json', auth='none', methods=['GET'], csrf=False)
    @authenticate_api
    def get_material(self, material_id, **kwargs):
        """
        Get a single material by ID
        """
        try:
            material = request.env['material.register'].browse(material_id)
            if not material.exists():
                return invalid_response(
                    message=f"Material with ID {material_id} not found",
                    code="MATERIAL_NOT_FOUND",
                    status=404
                )
            
            # Prepare response with detailed material information
            material_data = {
                'id': material.id,
                'material_code': material.material_code,
                'name': material.name,
                'material_type': material.material_type,
                'material_buy_price': float(material.material_buy_price),
                'currency': {
                    'id': material.currency_id.id,
                    'name': material.currency_id.name,
                    'symbol': material.currency_id.symbol
                },
                'partner': {
                    'id': material.partner_id.id,
                    'name': material.partner_id.name,
                    'email': material.partner_id.email,
                    'phone': material.partner_id.phone
                },
                'create_date': serialize_date(material.create_date),
                'write_date': serialize_date(material.write_date),
                'create_uid': {
                    'id': material.create_uid.id,
                    'name': material.create_uid.name
                } if material.create_uid else None,
                'write_uid': {
                    'id': material.write_uid.id,
                    'name': material.write_uid.name
                } if material.write_uid else None
            }
            
            return valid_response(
                data=material_data,
                message=f"Material '{material.name}' retrieved successfully"
            )
        except Exception as e:
            _logger.exception(f"Error fetching material with ID {material_id}")
            return invalid_response(
                message=f"Failed to retrieve material with ID {material_id}",
                code="MATERIAL_FETCH_ERROR",
                status=500
            )
    
    @http.route('/api/v1/materials', type='json', auth='none', methods=['POST'], csrf=False)
    @authenticate_api
    def create_material(self, **kwargs):
        """
        Create a new material
        """
        try:
            # Define required fields
            required_fields = ['material_code', 'name', 'material_type', 'material_buy_price', 'partner_id']
            
            # Get data from request - in JSON mode, all data is in kwargs
            post_data = {}
            for field in kwargs:
                post_data[field] = kwargs[field]
            
            # Validate required fields
            missing_fields = [field for field in required_fields if field not in post_data]
            if missing_fields:
                return invalid_response(
                    message=f"Missing required fields: {', '.join(missing_fields)}",
                    code="MISSING_REQUIRED_FIELDS",
                    status=400
                )
            
            # Validate material type
            allowed_types = ['fabric', 'jeans', 'cotton']
            if post_data.get('material_type') not in allowed_types:
                return invalid_response(
                    message=f"Invalid material type. Allowed values: {', '.join(allowed_types)}",
                    code="INVALID_MATERIAL_TYPE",
                    status=400
                )
            
            # Create new material
            new_material = request.env['material.register'].create({
                'material_code': post_data.get('material_code'),
                'name': post_data.get('name'),
                'material_type': post_data.get('material_type'),
                'material_buy_price': post_data.get('material_buy_price'),
                'partner_id': post_data.get('partner_id')
            })
            
            # Prepare response data
            response_data = {
                'id': new_material.id,
                'material_code': new_material.material_code,
                'name': new_material.name,
                'material_type': new_material.material_type,
                'material_buy_price': float(new_material.material_buy_price),
                'create_date': serialize_date(new_material.create_date)
            }
            
            return valid_response(
                data=response_data,
                message=f"Material '{new_material.name}' created successfully",
                status=201
            )
        except Exception as e:
            _logger.exception("Error creating material")
            return invalid_response(
                message=f"Failed to create material: {str(e)}",
                code="MATERIAL_CREATE_ERROR",
                status=500
            )
    
    @http.route('/api/v1/materials/<int:material_id>', type='json', auth='none', methods=['PUT'], csrf=False)
    @authenticate_api
    def update_material(self, material_id, **kwargs):
        """
        Update an existing material
        """
        try:
            # Check if material exists
            material = request.env['material.register'].browse(material_id)
            if not material.exists():
                return invalid_response(
                    message=f"Material with ID {material_id} not found",
                    code="MATERIAL_NOT_FOUND",
                    status=404
                )
            
            # Get data from request - in JSON mode, all data is in kwargs
            post_data = {}
            for field in kwargs:
                post_data[field] = kwargs[field]
                
            update_values = {}
            
            # Check which fields to update
            if 'material_code' in post_data:
                update_values['material_code'] = post_data.get('material_code')
                
            if 'name' in post_data:
                update_values['name'] = post_data.get('name')
                
            if 'material_type' in post_data:
                # Validate material type
                allowed_types = ['fabric', 'jeans', 'cotton']
                if post_data.get('material_type') not in allowed_types:
                    return invalid_response(
                        message=f"Invalid material type. Allowed values: {', '.join(allowed_types)}",
                        code="INVALID_MATERIAL_TYPE",
                        status=400
                    )
                update_values['material_type'] = post_data.get('material_type')
                
            if 'material_buy_price' in post_data:
                # Validate price is positive
                if float(post_data.get('material_buy_price', 0)) <= 0:
                    return invalid_response(
                        message="Material buy price must be positive",
                        code="INVALID_PRICE",
                        status=400
                    )
                update_values['material_buy_price'] = post_data.get('material_buy_price')
                
            if 'partner_id' in post_data:
                # Validate partner exists
                partner = request.env['res.partner'].browse(post_data.get('partner_id'))
                if not partner.exists():
                    return invalid_response(
                        message=f"Partner with ID {post_data.get('partner_id')} not found",
                        code="PARTNER_NOT_FOUND",
                        status=400
                    )
                update_values['partner_id'] = post_data.get('partner_id')
            
            # If no fields to update, return error
            if not update_values:
                return invalid_response(
                    message="No fields to update provided",
                    code="NO_UPDATE_DATA",
                    status=400
                )
            
            # Update material
            material.write(update_values)
            
            # Prepare response data
            response_data = {
                'id': material.id,
                'material_code': material.material_code,
                'name': material.name,
                'material_type': material.material_type,
                'material_buy_price': float(material.material_buy_price),
                'partner': {
                    'id': material.partner_id.id,
                    'name': material.partner_id.name
                },
                'write_date': serialize_date(material.write_date),
                'write_uid': {
                    'id': material.write_uid.id,
                    'name': material.write_uid.name
                } if material.write_uid else None
            }
            
            return valid_response(
                data=response_data,
                message=f"Material '{material.name}' updated successfully"
            )
        except Exception as e:
            _logger.exception(f"Error updating material with ID {material_id}")
            return invalid_response(
                message=f"Failed to update material: {str(e)}",
                code="MATERIAL_UPDATE_ERROR",
                status=500
            )
    
    @http.route('/api/v1/materials/<int:material_id>', type='json', auth='none', methods=['DELETE'], csrf=False)
    @authenticate_api
    def delete_material(self, material_id, **kwargs):
        """
        Delete a material by ID
        """
        try:
            # Check if material exists
            material = request.env['material.register'].browse(material_id)
            if not material.exists():
                return invalid_response(
                    message=f"Material with ID {material_id} not found",
                    code="MATERIAL_NOT_FOUND",
                    status=404
                )
            
            # Store material info before deletion for response
            material_info = {
                'id': material_id,
                'material_code': material.material_code,
                'name': material.name
            }
            
            # Delete material
            material.unlink()
            
            return valid_response(
                data={
                    'deleted': True,
                    'material': material_info
                },
                message=f"Material '{material_info['name']}' deleted successfully"
            )
        except Exception as e:
            _logger.exception(f"Error deleting material with ID {material_id}")
            return invalid_response(
                message=f"Failed to delete material: {str(e)}",
                code="MATERIAL_DELETE_ERROR",
                status=500
            )
