from flask import Blueprint, request, jsonify
from src.models.user import User
from src.routes.auth_middleware import token_required
import datetime
import json

client_data_bp = Blueprint("client_data", __name__)

# Simulated database for client data
client_profiles = []
client_metrics = []
client_attendance = []
client_reports = []

@client_data_bp.route("/profiles", methods=["GET"])
@token_required
def get_client_profiles(current_user):
    """Get all client profiles"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    # In a real implementation, this would query the database
    # Return simulated data for now
    return jsonify({"profiles": client_profiles}), 200

@client_data_bp.route("/profiles", methods=["POST"])
@token_required
def create_client_profile(current_user):
    """Create a new client profile with detailed information"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["firstName", "lastName", "email", "phone", "dateOfBirth"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    # Create new profile with unique ID
    new_profile = {
        "id": len(client_profiles) + 1,
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "email": data["email"],
        "phone": data["phone"],
        "dateOfBirth": data["dateOfBirth"],
        "address": data.get("address", ""),
        "city": data.get("city", ""),
        "postalCode": data.get("postalCode", ""),
        "country": data.get("country", "Switzerland"),
        "emergencyContact": data.get("emergencyContact", ""),
        "emergencyPhone": data.get("emergencyPhone", ""),
        "medicalNotes": data.get("medicalNotes", ""),
        "fitnessGoals": data.get("fitnessGoals", ""),
        "membershipType": data.get("membershipType", "Standard"),
        "memberSince": data.get("memberSince", datetime.datetime.now().strftime("%Y-%m-%d")),
        "referredBy": data.get("referredBy", None),
        "credits": data.get("credits", 0),
        "consentMarketing": data.get("consentMarketing", False),
        "consentPhotos": data.get("consentPhotos", False),
        "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    client_profiles.append(new_profile)
    return jsonify({"message": "Client profile created successfully", "profile": new_profile}), 201

@client_data_bp.route("/profiles/<int:profile_id>", methods=["GET"])
@token_required
def get_client_profile(current_user, profile_id):
    """Get a specific client profile by ID"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    # In a real implementation, this would query the database
    profile = next((p for p in client_profiles if p["id"] == profile_id), None)
    
    if not profile:
        return jsonify({"message": "Client profile not found"}), 404
        
    return jsonify({"profile": profile}), 200

@client_data_bp.route("/profiles/<int:profile_id>", methods=["PUT"])
@token_required
def update_client_profile(current_user, profile_id):
    """Update a client profile"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    data = request.get_json()
    
    # Find profile by ID
    profile_index = next((i for i, p in enumerate(client_profiles) if p["id"] == profile_id), None)
    
    if profile_index is None:
        return jsonify({"message": "Client profile not found"}), 404
    
    # Update profile fields
    for key, value in data.items():
        if key not in ["id", "createdAt"]:  # Protect certain fields
            client_profiles[profile_index][key] = value
    
    # Update timestamp
    client_profiles[profile_index]["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({"message": "Client profile updated successfully", "profile": client_profiles[profile_index]}), 200

@client_data_bp.route("/metrics", methods=["POST"])
@token_required
def record_client_metrics(current_user):
    """Record fitness metrics for a client"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["clientId", "metricType", "value"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    # Create new metric record
    new_metric = {
        "id": len(client_metrics) + 1,
        "clientId": data["clientId"],
        "metricType": data["metricType"],  # e.g., weight, bodyFat, strength, endurance
        "value": data["value"],
        "unit": data.get("unit", ""),
        "notes": data.get("notes", ""),
        "recordedBy": current_user.id,
        "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    client_metrics.append(new_metric)
    return jsonify({"message": "Client metric recorded successfully", "metric": new_metric}), 201

@client_data_bp.route("/metrics/<int:client_id>", methods=["GET"])
@token_required
def get_client_metrics(current_user, client_id):
    """Get all metrics for a specific client"""
    if not current_user.is_admin and not current_user.is_trainer and current_user.id != client_id:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    # Filter metrics by client ID
    metrics = [m for m in client_metrics if m["clientId"] == client_id]
    
    return jsonify({"metrics": metrics}), 200

@client_data_bp.route("/attendance", methods=["POST"])
@token_required
def record_attendance(current_user):
    """Record client attendance for a class"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["clientId", "classId"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    # Create new attendance record
    new_attendance = {
        "id": len(client_attendance) + 1,
        "clientId": data["clientId"],
        "classId": data["classId"],
        "status": data.get("status", "attended"),  # attended, late, cancelled, no-show
        "checkinTime": data.get("checkinTime", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "notes": data.get("notes", ""),
        "recordedBy": current_user.id
    }
    
    client_attendance.append(new_attendance)
    return jsonify({"message": "Attendance recorded successfully", "attendance": new_attendance}), 201

@client_data_bp.route("/attendance/<int:client_id>", methods=["GET"])
@token_required
def get_client_attendance(current_user, client_id):
    """Get attendance history for a specific client"""
    if not current_user.is_admin and not current_user.is_trainer and current_user.id != client_id:
        return jsonify({"message": "Insufficient permissions"}), 403
        
    # Filter attendance by client ID
    attendance = [a for a in client_attendance if a["clientId"] == client_id]
    
    return jsonify({"attendance": attendance}), 200

@client_data_bp.route("/reports/retention", methods=["GET"])
@token_required
def get_retention_report(current_user):
    """Generate retention rate report"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
    
    # In a real implementation, this would calculate actual retention metrics
    # For now, return simulated data
    retention_data = {
        "overall": 78.5,  # percentage
        "byMonth": [
            {"month": "January", "rate": 82.3},
            {"month": "February", "rate": 79.1},
            {"month": "March", "rate": 80.5},
            {"month": "April", "rate": 76.8},
            {"month": "May", "rate": 78.5}
        ],
        "byMembershipType": [
            {"type": "Standard", "rate": 75.2},
            {"type": "Premium", "rate": 86.7},
            {"type": "Corporate", "rate": 91.3},
            {"type": "Student", "rate": 68.9}
        ],
        "churnReasons": [
            {"reason": "Price", "percentage": 35},
            {"reason": "Relocation", "percentage": 25},
            {"reason": "Schedule", "percentage": 20},
            {"reason": "Facility", "percentage": 10},
            {"reason": "Other", "percentage": 10}
        ]
    }
    
    return jsonify({"report": retention_data}), 200

@client_data_bp.route("/reports/attendance", methods=["GET"])
@token_required
def get_attendance_report(current_user):
    """Generate class attendance report"""
    if not current_user.is_admin and not current_user.is_trainer:
        return jsonify({"message": "Insufficient permissions"}), 403
    
    # Get query parameters
    start_date = request.args.get("startDate", None)
    end_date = request.args.get("endDate", None)
    class_type = request.args.get("classType", None)
    
    # In a real implementation, this would filter based on parameters
    # For now, return simulated data
    attendance_data = {
        "overall": {
            "totalClasses": 120,
            "totalAttendees": 876,
            "averagePerClass": 7.3,
            "capacityUtilization": 72.5  # percentage
        },
        "byDay": [
            {"day": "Monday", "average": 8.2},
            {"day": "Tuesday", "average": 7.5},
            {"day": "Wednesday", "average": 8.1},
            {"day": "Thursday", "average": 7.8},
            {"day": "Friday", "average": 6.9},
            {"day": "Saturday", "average": 9.3},
            {"day": "Sunday", "average": 4.2}
        ],
        "byTime": [
            {"time": "06:00-08:00", "average": 6.8},
            {"time": "08:00-12:00", "average": 5.2},
            {"time": "12:00-14:00", "average": 7.9},
            {"time": "14:00-18:00", "average": 6.1},
            {"time": "18:00-22:00", "average": 9.4}
        ],
        "byType": [
            {"type": "HIIT", "average": 8.7},
            {"type": "Yoga", "average": 7.2},
            {"type": "Strength", "average": 8.1},
            {"type": "Cardio", "average": 7.5},
            {"type": "Pilates", "average": 6.8}
        ],
        "topClasses": [
            {"name": "Evening HIIT", "average": 9.8},
            {"name": "Morning Yoga", "average": 9.2},
            {"name": "Power Strength", "average": 8.9},
            {"name": "Cardio Blast", "average": 8.7},
            {"name": "Core Pilates", "average": 8.5}
        ]
    }
    
    return jsonify({"report": attendance_data}), 200

@client_data_bp.route("/reports/custom", methods=["POST"])
@token_required
def generate_custom_report(current_user):
    """Generate custom report based on specified parameters"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    
    # Validate required fields
    if "reportType" not in data:
        return jsonify({"message": "Missing required field: reportType"}), 400
    
    report_type = data["reportType"]
    parameters = data.get("parameters", {})
    
    # Create new report record
    new_report = {
        "id": len(client_reports) + 1,
        "reportType": report_type,
        "parameters": parameters,
        "generatedBy": current_user.id,
        "generatedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "completed"
    }
    
    # Generate report data based on type
    if report_type == "memberActivity":
        new_report["data"] = generate_member_activity_report(parameters)
    elif report_type == "financialSummary":
        new_report["data"] = generate_financial_summary_report(parameters)
    elif report_type == "trainerPerformance":
        new_report["data"] = generate_trainer_performance_report(parameters)
    else:
        return jsonify({"message": f"Unsupported report type: {report_type}"}), 400
    
    client_reports.append(new_report)
    return jsonify({"message": "Report generated successfully", "report": new_report}), 201

@client_data_bp.route("/reports", methods=["GET"])
@token_required
def get_reports(current_user):
    """Get all generated reports"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    return jsonify({"reports": client_reports}), 200

@client_data_bp.route("/reports/<int:report_id>", methods=["GET"])
@token_required
def get_report(current_user, report_id):
    """Get a specific report by ID"""
    if not current_user.is_admin:
        return jsonify({"message": "Admin privileges required"}), 403
        
    # Find report by ID
    report = next((r for r in client_reports if r["id"] == report_id), None)
    
    if not report:
        return jsonify({"message": "Report not found"}), 404
        
    return jsonify({"report": report}), 200

# Helper functions for report generation
def generate_member_activity_report(parameters):
    """Generate member activity report with simulated data"""
    return {
        "activeMembers": 127,
        "newMembers": 15,
        "churned": 8,
        "averageClassesPerMember": 2.3,
        "mostActiveMembers": [
            {"id": 12, "name": "John Smith", "classes": 12},
            {"id": 45, "name": "Sarah Johnson", "classes": 10},
            {"id": 23, "name": "Michael Brown", "classes": 9}
        ],
        "leastActiveMembers": [
            {"id": 78, "name": "David Wilson", "classes": 0},
            {"id": 56, "name": "Emma Davis", "classes": 1},
            {"id": 34, "name": "James Miller", "classes": 1}
        ]
    }

def generate_financial_summary_report(parameters):
    """Generate financial summary report with simulated data"""
    return {
        "totalRevenue": 24750,
        "membershipRevenue": 18500,
        "classRevenue": 4250,
        "otherRevenue": 2000,
        "revenueByMonth": [
            {"month": "January", "amount": 4800},
            {"month": "February", "amount": 4950},
            {"month": "March", "amount": 5100},
            {"month": "April", "amount": 4900},
            {"month": "May", "amount": 5000}
        ],
        "revenueByMembershipType": [
            {"type": "Standard", "amount": 8200},
            {"type": "Premium", "amount": 7500},
            {"type": "Corporate", "amount": 2800},
            {"type": "Student", "amount": 2000}
        ]
    }

def generate_trainer_performance_report(parameters):
    """Generate trainer performance report with simulated data"""
    return {
        "trainers": [
            {
                "id": 1,
                "name": "Alex Johnson",
                "classesLed": 45,
                "totalAttendees": 382,
                "averageRating": 4.8,
                "attendanceRate": 92.5
            },
            {
                "id": 2,
                "name": "Maria Garcia",
                "classesLed": 38,
                "totalAttendees": 315,
                "averageRating": 4.7,
                "attendanceRate": 89.3
            },
            {
                "id": 3,
                "name": "Thomas Lee",
                "classesLed": 42,
                "totalAttendees": 356,
                "averageRating": 4.6,
                "attendanceRate": 90.1
            }
        ],
        "topClasses": [
            {"trainer": "Alex Johnson", "class": "HIIT Extreme", "averageAttendance": 9.2},
            {"trainer": "Maria Garcia", "class": "Power Yoga", "averageAttendance": 8.9},
            {"trainer": "Thomas Lee", "class": "Strength Circuit", "averageAttendance": 8.7}
        ]
    }
