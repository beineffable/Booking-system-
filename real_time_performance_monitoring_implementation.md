# Real-Time Performance Monitoring Implementation

## Overview

This document outlines the implementation approach for real-time performance monitoring within the Training Club Fitness Platform. This system will provide actionable insights during and after classes, connecting analytics, automation, and trainer tools to enhance the training experience and outcomes.

## Core Components

### 1. Performance Data Collection System

```python
class PerformanceDataCollector:
    def __init__(self, db_connection, data_sources_manager):
        self.db = db_connection
        self.data_sources = data_sources_manager  # Manages connections to various data sources
        self.active_collection_sessions = {}  # Tracks active collection sessions by class_id
    
    def start_class_collection(self, class_id, trainer_id, class_type, expected_members=None):
        """Start collecting performance data for a class session"""
        if class_id in self.active_collection_sessions:
            return {"success": False, "reason": "Collection already active for this class"}
            
        # Initialize collection session
        session = {
            "class_id": class_id,
            "trainer_id": trainer_id,
            "class_type": class_type,
            "start_time": datetime.now(),
            "expected_members": expected_members or self.db.get_class_registrations(class_id),
            "data_sources": self._initialize_data_sources(class_type),
            "collected_data": {},
            "status": "active"
        }
        
        # Start data collection from each source
        for source_id, source in session["data_sources"].items():
            try:
                source.start_collection(class_id)
                print(f"Started collection from {source_id} for class {class_id}")
            except Exception as e:
                print(f"Error starting collection from {source_id}: {str(e)}")
                # Continue with other sources even if one fails
        
        self.active_collection_sessions[class_id] = session
        
        # Log collection start
        self.db.log_performance_collection_event(class_id, "start", {
            "trainer_id": trainer_id,
            "expected_members": len(session["expected_members"]),
            "active_sources": list(session["data_sources"].keys())
        })
        
        return {"success": True, "session_info": self._get_session_public_info(session)}
    
    def end_class_collection(self, class_id):
        """End data collection for a class session"""
        if class_id not in self.active_collection_sessions:
            return {"success": False, "reason": "No active collection for this class"}
            
        session = self.active_collection_sessions[class_id]
        
        # Stop data collection from each source
        for source_id, source in session["data_sources"].items():
            try:
                final_data = source.stop_collection(class_id)
                session["collected_data"][source_id] = final_data
                print(f"Stopped collection from {source_id} for class {class_id}")
            except Exception as e:
                print(f"Error stopping collection from {source_id}: {str(e)}")
        
        session["end_time"] = datetime.now()
        session["status"] = "completed"
        
        # Process and store the collected data
        processed_data = self._process_collected_data(session)
        performance_record_id = self.db.store_class_performance_data(class_id, processed_data)
        
        # Generate summary
        summary = self._generate_performance_summary(processed_data)
        summary_id = self.db.store_performance_summary(class_id, summary)
        
        # Log collection end
        self.db.log_performance_collection_event(class_id, "end", {
            "duration_minutes": (session["end_time"] - session["start_time"]).total_seconds() / 60,
            "performance_record_id": performance_record_id,
            "summary_id": summary_id
        })
        
        # Remove from active sessions
        del self.active_collection_sessions[class_id]
        
        return {
            "success": True, 
            "performance_record_id": performance_record_id,
            "summary_id": summary_id,
            "summary": summary
        }
    
    def get_real_time_snapshot(self, class_id):
        """Get current performance snapshot for an active class"""
        if class_id not in self.active_collection_sessions:
            return {"success": False, "reason": "No active collection for this class"}
            
        session = self.active_collection_sessions[class_id]
        snapshot_data = {}
        
        # Get current data from each source
        for source_id, source in session["data_sources"].items():
            try:
                current_data = source.get_current_data(class_id)
                snapshot_data[source_id] = current_data
            except Exception as e:
                print(f"Error getting current data from {source_id}: {str(e)}")
                snapshot_data[source_id] = {"error": str(e)}
        
        # Process the snapshot data
        processed_snapshot = self._process_snapshot_data(snapshot_data, session)
        
        # Generate insights from the snapshot
        insights = self._generate_real_time_insights(processed_snapshot, session)
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "class_duration_minutes": (datetime.now() - session["start_time"]).total_seconds() / 60,
            "metrics": processed_snapshot,
            "insights": insights
        }
    
    def _initialize_data_sources(self, class_type):
        """Initialize appropriate data sources based on class type"""
        available_sources = self.data_sources.get_available_sources()
        appropriate_sources = {}
        
        # Logic to determine which sources are appropriate for this class type
        for source_id, source in available_sources.items():
            if source.is_applicable_for_class_type(class_type):
                appropriate_sources[source_id] = source
        
        return appropriate_sources
    
    def _process_collected_data(self, session):
        """Process raw collected data into structured performance data"""
        processed_data = {
            "class_id": session["class_id"],
            "trainer_id": session["trainer_id"],
            "class_type": session["class_type"],
            "start_time": session["start_time"].isoformat(),
            "end_time": session["end_time"].isoformat(),
            "duration_minutes": (session["end_time"] - session["start_time"]).total_seconds() / 60,
            "member_data": {},
            "aggregate_data": {}
        }
        
        # Process data for each member
        for member in session["expected_members"]:
            member_id = member["member_id"]
            member_data = self._extract_member_data(member_id, session["collected_data"])
            if member_data:
                processed_data["member_data"][member_id] = member_data
        
        # Calculate aggregate metrics
        processed_data["aggregate_data"] = self._calculate_aggregate_metrics(processed_data["member_data"])
        
        return processed_data
    
    def _extract_member_data(self, member_id, collected_data):
        """Extract data for a specific member from all sources"""
        member_data = {}
        
        for source_id, source_data in collected_data.items():
            if member_id in source_data.get("member_data", {}):
                member_data[source_id] = source_data["member_data"][member_id]
        
        # If no data found for this member, they might not have attended
        if not member_data:
            return None
            
        # Calculate derived metrics
        member_data["derived_metrics"] = self._calculate_derived_metrics(member_data)
        
        return member_data
    
    def _calculate_derived_metrics(self, member_data):
        """Calculate derived performance metrics from raw source data"""
        # Example derived metrics
        derived = {}
        
        # Example: Calculate average heart rate if heart rate data exists
        if "heart_rate_monitor" in member_data and "heart_rate_samples" in member_data["heart_rate_monitor"]:
            samples = member_data["heart_rate_monitor"]["heart_rate_samples"]
            if samples:
                derived["avg_heart_rate"] = sum(sample["value"] for sample in samples) / len(samples)
                derived["max_heart_rate"] = max(sample["value"] for sample in samples)
        
        # Example: Calculate workout intensity score
        intensity_factors = []
        if "avg_heart_rate" in derived:
            # Assume max HR is 220 - age, but we don't have age, so use a placeholder
            intensity_factors.append(derived["avg_heart_rate"] / 170)  # Placeholder
        
        if intensity_factors:
            derived["intensity_score"] = sum(intensity_factors) / len(intensity_factors) * 10  # Scale to 0-10
        
        return derived
    
    def _calculate_aggregate_metrics(self, all_member_data):
        """Calculate aggregate metrics across all members"""
        if not all_member_data:
            return {}
            
        aggregate = {
            "member_count": len(all_member_data),
            "avg_metrics": {}
        }
        
        # Collect all derived metrics
        all_derived = {}
        for member_id, data in all_member_data.items():
            if "derived_metrics" in data:
                for metric, value in data["derived_metrics"].items():
                    if metric not in all_derived:
                        all_derived[metric] = []
                    all_derived[metric].append(value)
        
        # Calculate averages
        for metric, values in all_derived.items():
            if values:
                aggregate["avg_metrics"][metric] = sum(values) / len(values)
        
        return aggregate
    
    def _process_snapshot_data(self, snapshot_data, session):
        """Process real-time snapshot data"""
        processed = {
            "member_metrics": {},
            "class_metrics": {}
        }
        
        # Process member-specific data
        for source_id, source_snapshot in snapshot_data.items():
            if "member_data" in source_snapshot:
                for member_id, member_metrics in source_snapshot["member_data"].items():
                    if member_id not in processed["member_metrics"]:
                        processed["member_metrics"][member_id] = {}
                    processed["member_metrics"][member_id][source_id] = member_metrics
        
        # Calculate real-time derived metrics for each member
        for member_id, sources in processed["member_metrics"].items():
            processed["member_metrics"][member_id]["derived"] = self._calculate_real_time_derived_metrics(sources)
        
        # Calculate class-level metrics
        active_members = len(processed["member_metrics"])
        processed["class_metrics"]["active_members"] = active_members
        processed["class_metrics"]["attendance_rate"] = active_members / len(session["expected_members"]) if session["expected_members"] else 0
        
        # Aggregate member metrics to class level
        if processed["member_metrics"]:
            derived_metrics = {}
            for member_id, member_data in processed["member_metrics"].items():
                if "derived" in member_data:
                    for metric, value in member_data["derived"].items():
                        if metric not in derived_metrics:
                            derived_metrics[metric] = []
                        derived_metrics[metric].append(value)
            
            # Calculate averages
            for metric, values in derived_metrics.items():
                if values:
                    processed["class_metrics"][f"avg_{metric}"] = sum(values) / len(values)
        
        return processed
    
    def _generate_real_time_insights(self, processed_snapshot, session):
        """Generate actionable insights from real-time data"""
        insights = []
        
        # Example insights based on class metrics
        class_metrics = processed_snapshot["class_metrics"]
        
        # Check attendance rate
        if class_metrics.get("attendance_rate", 1) < 0.7:
            insights.append({
                "type": "attendance",
                "severity": "medium",
                "message": f"Low attendance rate ({class_metrics['attendance_rate']*100:.0f}%). Consider following up with absent members."
            })
        
        # Check intensity level
        if "avg_intensity_score" in class_metrics:
            if class_metrics["avg_intensity_score"] < 3:
                insights.append({
                    "type": "intensity",
                    "severity": "medium",
                    "message": "Class intensity is lower than expected. Consider increasing challenge level."
                })
            elif class_metrics["avg_intensity_score"] > 8:
                insights.append({
                    "type": "intensity",
                    "severity": "medium",
                    "message": "Class intensity is very high. Monitor for signs of overexertion."
                })
        
        # Check for members who might need attention
        for member_id, metrics in processed_snapshot["member_metrics"].items():
            if "derived" in metrics:
                derived = metrics["derived"]
                
                # Example: Check if heart rate is too high
                if derived.get("heart_rate", 0) > 180:
                    member_name = self._get_member_name(member_id, session["expected_members"])
                    insights.append({
                        "type": "member_alert",
                        "severity": "high",
                        "member_id": member_id,
                        "member_name": member_name,
                        "message": f"{member_name} has a very high heart rate ({derived['heart_rate']}). Check on them."
                    })
        
        return insights
    
    def _generate_performance_summary(self, processed_data):
        """Generate a summary of the class performance"""
        summary = {
            "class_id": processed_data["class_id"],
            "class_type": processed_data["class_type"],
            "date": processed_data["start_time"].split("T")[0],
            "duration_minutes": processed_data["duration_minutes"],
            "attendance": {
                "expected": len(processed_data.get("expected_members", [])),
                "actual": len(processed_data["member_data"])
            },
            "intensity": {
                "average": processed_data["aggregate_data"].get("avg_metrics", {}).get("intensity_score", None),
                "distribution": self._calculate_intensity_distribution(processed_data["member_data"])
            },
            "performance_highlights": self._identify_performance_highlights(processed_data),
            "improvement_areas": self._identify_improvement_areas(processed_data),
            "member_achievements": self._identify_member_achievements(processed_data)
        }
        
        return summary
    
    def _calculate_intensity_distribution(self, member_data):
        """Calculate the distribution of intensity levels"""
        distribution = {
            "low": 0,
            "medium": 0,
            "high": 0
        }
        
        for member_id, data in member_data.items():
            if "derived_metrics" in data and "intensity_score" in data["derived_metrics"]:
                score = data["derived_metrics"]["intensity_score"]
                if score < 4:
                    distribution["low"] += 1
                elif score < 7:
                    distribution["medium"] += 1
                else:
                    distribution["high"] += 1
        
        return distribution
    
    def _identify_performance_highlights(self, processed_data):
        """Identify notable performance aspects"""
        highlights = []
        
        # Example: High overall intensity
        avg_intensity = processed_data["aggregate_data"].get("avg_metrics", {}).get("intensity_score")
        if avg_intensity and avg_intensity > 7:
            highlights.append({
                "type": "high_intensity",
                "message": f"High overall class intensity ({avg_intensity:.1f}/10)"
            })
        
        # Example: Good attendance
        expected = len(processed_data.get("expected_members", []))
        actual = len(processed_data["member_data"])
        if expected > 0 and actual / expected > 0.9:
            highlights.append({
                "type": "high_attendance",
                "message": f"Excellent attendance rate ({actual}/{expected} members, {actual/expected*100:.0f}%)"
            })
        
        return highlights
    
    def _identify_improvement_areas(self, processed_data):
        """Identify areas that could be improved"""
        areas = []
        
        # Example: Low attendance
        expected = len(processed_data.get("expected_members", []))
        actual = len(processed_data["member_data"])
        if expected > 0 and actual / expected < 0.7:
            areas.append({
                "type": "low_attendance",
                "message": f"Low attendance rate ({actual}/{expected} members, {actual/expected*100:.0f}%)"
            })
        
        # Example: Inconsistent intensity
        intensity_distribution = self._calculate_intensity_distribution(processed_data["member_data"])
        total_members = sum(intensity_distribution.values())
        if total_members > 0:
            max_category = max(intensity_distribution, key=intensity_distribution.get)
            max_percentage = intensity_distribution[max_category] / total_members
            if max_percentage < 0.5 and total_members > 3:
                areas.append({
                    "type": "inconsistent_intensity",
                    "message": "Wide variation in member intensity levels. Consider more personalized instruction."
                })
        
        return areas
    
    def _identify_member_achievements(self, processed_data):
        """Identify individual member achievements"""
        achievements = []
        
        for member_id, data in processed_data["member_data"].items():
            if "derived_metrics" in data:
                metrics = data["derived_metrics"]
                
                # Example: High intensity achievement
                if metrics.get("intensity_score", 0) > 8:
                    member_name = self._get_member_name(member_id, processed_data.get("expected_members", []))
                    achievements.append({
                        "member_id": member_id,
                        "member_name": member_name,
                        "type": "high_intensity",
                        "message": f"{member_name} maintained very high intensity throughout class"
                    })
                
                # Could add more achievement types
        
        return achievements
    
    def _get_member_name(self, member_id, expected_members):
        """Get member name from expected members list"""
        for member in expected_members:
            if member.get("member_id") == member_id:
                return member.get("name", f"Member {member_id}")
        return f"Member {member_id}"
    
    def _get_session_public_info(self, session):
        """Get shareable session info (without internal details)"""
        return {
            "class_id": session["class_id"],
            "trainer_id": session["trainer_id"],
            "class_type": session["class_type"],
            "start_time": session["start_time"].isoformat(),
            "expected_member_count": len(session["expected_members"]),
            "active_data_sources": list(session["data_sources"].keys()),
            "status": session["status"]
        }
```

### 2. Data Sources Manager

```python
class DataSourcesManager:
    def __init__(self, db_connection, config=None):
        self.db = db_connection
        self.config = config or {}
        self.available_sources = {}
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize all configured data sources"""
        # Initialize built-in sources
        self._initialize_built_in_sources()
        
        # Initialize external sources from config
        self._initialize_external_sources()
        
        print(f"Initialized {len(self.available_sources)} data sources")
    
    def _initialize_built_in_sources(self):
        """Initialize built-in data sources"""
        # Manual Tracking Source (always available)
        self.available_sources["manual_tracking"] = ManualTrackingSource(self.db)
        
        # App Check-in Source (always available)
        self.available_sources["app_checkin"] = AppCheckinSource(self.db)
        
        # Trainer Input Source (always available)
        self.available_sources["trainer_input"] = TrainerInputSource(self.db)
    
    def _initialize_external_sources(self):
        """Initialize external data sources from configuration"""
        external_sources = self.config.get("external_sources", [])
        
        for source_config in external_sources:
            source_type = source_config.get("type")
            source_id = source_config.get("id")
            
            if not source_type or not source_id:
                print(f"Skipping invalid source config: {source_config}")
                continue
            
            try:
                if source_type == "heart_rate_monitor":
                    self.available_sources[source_id] = HeartRateMonitorSource(self.db, source_config)
                elif source_type == "movement_sensor":
                    self.available_sources[source_id] = MovementSensorSource(self.db, source_config)
                elif source_type == "wearable_integration":
                    self.available_sources[source_id] = WearableIntegrationSource(self.db, source_config)
                else:
                    print(f"Unknown source type: {source_type}")
            except Exception as e:
                print(f"Error initializing source {source_id} of type {source_type}: {str(e)}")
    
    def get_available_sources(self):
        """Get all available data sources"""
        return self.available_sources
    
    def get_source(self, source_id):
        """Get a specific data source by ID"""
        return self.available_sources.get(source_id)
```

### 3. Built-in Data Source Implementations

```python
class BaseDataSource:
    """Base class for all data sources"""
    def __init__(self, db_connection):
        self.db = db_connection
        self.active_collections = set()  # Set of class_ids with active collection
    
    def start_collection(self, class_id):
        """Start collecting data for a class"""
        if class_id in self.active_collections:
            raise ValueError(f"Collection already active for class {class_id}")
        
        self.active_collections.add(class_id)
        return True
    
    def stop_collection(self, class_id):
        """Stop collecting data for a class and return final data"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        self.active_collections.remove(class_id)
        return self._get_collected_data(class_id)
    
    def get_current_data(self, class_id):
        """Get current data snapshot for an active class"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        return self._get_current_data_snapshot(class_id)
    
    def is_applicable_for_class_type(self, class_type):
        """Check if this source is applicable for a class type"""
        # Default implementation: applicable to all class types
        return True
    
    def _get_collected_data(self, class_id):
        """Get all collected data for a class (implementation specific)"""
        raise NotImplementedError("Subclasses must implement _get_collected_data")
    
    def _get_current_data_snapshot(self, class_id):
        """Get current data snapshot (implementation specific)"""
        raise NotImplementedError("Subclasses must implement _get_current_data_snapshot")


class ManualTrackingSource(BaseDataSource):
    """Source for manually tracked data (e.g., trainer observations)"""
    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.tracked_data = {}  # class_id -> tracked data
    
    def start_collection(self, class_id):
        super().start_collection(class_id)
        self.tracked_data[class_id] = {
            "observations": [],
            "member_ratings": {}
        }
        return True
    
    def add_observation(self, class_id, observation_type, observation_data):
        """Add a manual observation"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        observation = {
            "type": observation_type,
            "data": observation_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.tracked_data[class_id]["observations"].append(observation)
        return True
    
    def add_member_rating(self, class_id, member_id, rating_type, rating_value):
        """Add a rating for a specific member"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        if member_id not in self.tracked_data[class_id]["member_ratings"]:
            self.tracked_data[class_id]["member_ratings"][member_id] = {}
        
        self.tracked_data[class_id]["member_ratings"][member_id][rating_type] = {
            "value": rating_value,
            "timestamp": datetime.now().isoformat()
        }
        
        return True
    
    def _get_collected_data(self, class_id):
        """Get all manually tracked data for a class"""
        data = self.tracked_data.get(class_id, {
            "observations": [],
            "member_ratings": {}
        })
        
        # Format for the collector
        return {
            "source_type": "manual_tracking",
            "observations": data["observations"],
            "member_data": {
                member_id: {"ratings": ratings}
                for member_id, ratings in data["member_ratings"].items()
            }
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current manually tracked data"""
        return self._get_collected_data(class_id)


class AppCheckinSource(BaseDataSource):
    """Source for member app check-ins and feedback"""
    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.checkin_data = {}  # class_id -> checkin data
    
    def start_collection(self, class_id):
        super().start_collection(class_id)
        self.checkin_data[class_id] = {
            "member_checkins": {},
            "member_feedback": {}
        }
        return True
    
    def record_member_checkin(self, class_id, member_id, checkin_time=None):
        """Record a member checking in to class"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        checkin_time = checkin_time or datetime.now()
        
        self.checkin_data[class_id]["member_checkins"][member_id] = {
            "checkin_time": checkin_time.isoformat(),
            "status": "checked_in"
        }
        
        return True
    
    def record_member_checkout(self, class_id, member_id, checkout_time=None):
        """Record a member checking out of class"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        if member_id not in self.checkin_data[class_id]["member_checkins"]:
            raise ValueError(f"Member {member_id} not checked in to class {class_id}")
        
        checkout_time = checkout_time or datetime.now()
        
        self.checkin_data[class_id]["member_checkins"][member_id].update({
            "checkout_time": checkout_time.isoformat(),
            "status": "checked_out",
            "duration_minutes": (checkout_time - datetime.fromisoformat(
                self.checkin_data[class_id]["member_checkins"][member_id]["checkin_time"]
            )).total_seconds() / 60
        })
        
        return True
    
    def record_member_feedback(self, class_id, member_id, feedback_data):
        """Record feedback from a member"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "data": feedback_data
        }
        
        self.checkin_data[class_id]["member_feedback"][member_id] = feedback
        
        return True
    
    def _get_collected_data(self, class_id):
        """Get all app checkin data for a class"""
        data = self.checkin_data.get(class_id, {
            "member_checkins": {},
            "member_feedback": {}
        })
        
        # Format for the collector
        member_data = {}
        for member_id, checkin in data["member_checkins"].items():
            member_data[member_id] = {
                "checkin": checkin
            }
            if member_id in data["member_feedback"]:
                member_data[member_id]["feedback"] = data["member_feedback"][member_id]
        
        return {
            "source_type": "app_checkin",
            "member_data": member_data
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current app checkin data"""
        return self._get_collected_data(class_id)


class TrainerInputSource(BaseDataSource):
    """Source for real-time trainer inputs during class"""
    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.trainer_inputs = {}  # class_id -> trainer inputs
    
    def start_collection(self, class_id):
        super().start_collection(class_id)
        self.trainer_inputs[class_id] = {
            "class_notes": [],
            "member_notes": {},
            "class_markers": []
        }
        return True
    
    def add_class_note(self, class_id, note_text, note_type="general"):
        """Add a note about the entire class"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        note = {
            "type": note_type,
            "text": note_text,
            "timestamp": datetime.now().isoformat()
        }
        
        self.trainer_inputs[class_id]["class_notes"].append(note)
        return True
    
    def add_member_note(self, class_id, member_id, note_text, note_type="general"):
        """Add a note about a specific member"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        if member_id not in self.trainer_inputs[class_id]["member_notes"]:
            self.trainer_inputs[class_id]["member_notes"][member_id] = []
        
        note = {
            "type": note_type,
            "text": note_text,
            "timestamp": datetime.now().isoformat()
        }
        
        self.trainer_inputs[class_id]["member_notes"][member_id].append(note)
        return True
    
    def add_class_marker(self, class_id, marker_type, marker_data=None):
        """Add a time marker for the class (e.g., "warmup_end", "main_workout_start")"""
        if class_id not in self.active_collections:
            raise ValueError(f"No active collection for class {class_id}")
        
        marker = {
            "type": marker_type,
            "data": marker_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.trainer_inputs[class_id]["class_markers"].append(marker)
        return True
    
    def _get_collected_data(self, class_id):
        """Get all trainer input data for a class"""
        data = self.trainer_inputs.get(class_id, {
            "class_notes": [],
            "member_notes": {},
            "class_markers": []
        })
        
        # Format for the collector
        member_data = {}
        for member_id, notes in data["member_notes"].items():
            member_data[member_id] = {
                "notes": notes
            }
        
        return {
            "source_type": "trainer_input",
            "class_notes": data["class_notes"],
            "class_markers": data["class_markers"],
            "member_data": member_data
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current trainer input data"""
        return self._get_collected_data(class_id)
```

### 4. External Data Source Implementations (Conceptual)

```python
class HeartRateMonitorSource(BaseDataSource):
    """Source for heart rate monitor data"""
    def __init__(self, db_connection, config):
        super().__init__(db_connection)
        self.config = config
        self.device_id = config.get("device_id")
        self.connection_params = config.get("connection_params", {})
        self.heart_rate_data = {}  # class_id -> heart rate data
        
        # In a real implementation, this would connect to the actual device/API
        print(f"Initialized heart rate monitor source: {self.device_id}")
    
    def start_collection(self, class_id):
        super().start_collection(class_id)
        self.heart_rate_data[class_id] = {
            "member_data": {}
        }
        
        # In a real implementation, this would start the actual data collection
        print(f"Started heart rate data collection for class {class_id}")
        return True
    
    def stop_collection(self, class_id):
        # In a real implementation, this would stop the actual data collection
        print(f"Stopped heart rate data collection for class {class_id}")
        return super().stop_collection(class_id)
    
    def _get_collected_data(self, class_id):
        """Get all heart rate data for a class"""
        # In a real implementation, this would retrieve the actual collected data
        # For this example, we'll return simulated data
        
        data = self.heart_rate_data.get(class_id, {"member_data": {}})
        
        # If no real data, generate simulated data for demonstration
        if not data["member_data"]:
            # Simulate data for 3 members
            for member_id in [101, 102, 103]:
                # Generate 10 heart rate samples
                samples = []
                for i in range(10):
                    samples.append({
                        "timestamp": (datetime.now() - timedelta(minutes=30) + timedelta(minutes=3*i)).isoformat(),
                        "value": random.randint(120, 160)
                    })
                
                data["member_data"][member_id] = {
                    "heart_rate_samples": samples,
                    "avg_heart_rate": sum(s["value"] for s in samples) / len(samples)
                }
        
        return {
            "source_type": "heart_rate_monitor",
            "device_id": self.device_id,
            "member_data": data["member_data"]
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current heart rate data"""
        # In a real implementation, this would get the latest data from the device/API
        # For this example, we'll return simulated data
        
        snapshot = {
            "source_type": "heart_rate_monitor",
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "member_data": {}
        }
        
        # Simulate data for 3 members
        for member_id in [101, 102, 103]:
            snapshot["member_data"][member_id] = {
                "heart_rate": random.randint(120, 160)
            }
        
        return snapshot
    
    def is_applicable_for_class_type(self, class_type):
        """Check if heart rate monitoring is applicable for this class type"""
        # Example: applicable for cardio and HIIT classes
        cardio_classes = ["cardio", "hiit", "spinning", "running"]
        return any(cardio_type in class_type.lower() for cardio_type in cardio_classes)


class MovementSensorSource(BaseDataSource):
    """Source for movement sensor data (e.g., rep counting, form analysis)"""
    def __init__(self, db_connection, config):
        super().__init__(db_connection)
        self.config = config
        self.sensor_id = config.get("sensor_id")
        self.connection_params = config.get("connection_params", {})
        self.movement_data = {}  # class_id -> movement data
        
        # In a real implementation, this would connect to the actual sensors/API
        print(f"Initialized movement sensor source: {self.sensor_id}")
    
    # Implementation similar to HeartRateMonitorSource, adapted for movement data
    # Methods would include start_collection, stop_collection, etc.
    
    def _get_collected_data(self, class_id):
        """Get all movement data for a class"""
        # Simulated data for demonstration
        return {
            "source_type": "movement_sensor",
            "sensor_id": self.sensor_id,
            "member_data": {
                # Simulated data for member 101
                101: {
                    "rep_count": 45,
                    "form_score": 0.85,
                    "movement_patterns": [
                        {"type": "squat", "count": 15, "avg_depth": 0.8, "form_score": 0.9},
                        {"type": "pushup", "count": 20, "avg_depth": 0.7, "form_score": 0.8},
                        {"type": "lunge", "count": 10, "avg_depth": 0.75, "form_score": 0.85}
                    ]
                },
                # Additional members would be included here
            }
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current movement data snapshot"""
        # Simulated data for demonstration
        return {
            "source_type": "movement_sensor",
            "sensor_id": self.sensor_id,
            "timestamp": datetime.now().isoformat(),
            "member_data": {
                101: {
                    "current_exercise": "squat",
                    "rep_count": 8,
                    "form_score": 0.85
                },
                102: {
                    "current_exercise": "pushup",
                    "rep_count": 12,
                    "form_score": 0.75
                }
            }
        }
    
    def is_applicable_for_class_type(self, class_type):
        """Check if movement sensing is applicable for this class type"""
        # Example: applicable for strength and functional training classes
        strength_classes = ["strength", "weight", "functional", "crossfit"]
        return any(strength_type in class_type.lower() for strength_type in strength_classes)


class WearableIntegrationSource(BaseDataSource):
    """Source for data from wearable devices (e.g., Apple Watch, Fitbit)"""
    def __init__(self, db_connection, config):
        super().__init__(db_connection)
        self.config = config
        self.integration_id = config.get("integration_id")
        self.provider = config.get("provider")  # e.g., "apple_health", "fitbit"
        self.wearable_data = {}  # class_id -> wearable data
        
        # In a real implementation, this would set up API connections
        print(f"Initialized wearable integration source: {self.integration_id} ({self.provider})")
    
    # Implementation similar to other sources, adapted for wearable data
    # Methods would include start_collection, stop_collection, etc.
    
    def _get_collected_data(self, class_id):
        """Get all wearable data for a class"""
        # Simulated data for demonstration
        return {
            "source_type": "wearable",
            "provider": self.provider,
            "member_data": {
                # Simulated data for member 101
                101: {
                    "device_type": "apple_watch",
                    "calories_burned": 320,
                    "avg_heart_rate": 142,
                    "steps": 2800,
                    "active_minutes": 45
                },
                # Additional members would be included here
            }
        }
    
    def _get_current_data_snapshot(self, class_id):
        """Get current wearable data snapshot"""
        # Simulated data for demonstration
        return {
            "source_type": "wearable",
            "provider": self.provider,
            "timestamp": datetime.now().isoformat(),
            "member_data": {
                101: {
                    "current_heart_rate": 145,
                    "calories_burned_so_far": 220,
                    "steps_so_far": 1900
                },
                102: {
                    "current_heart_rate": 132,
                    "calories_burned_so_far": 180,
                    "steps_so_far": 1700
                }
            }
        }
    
    def is_applicable_for_class_type(self, class_type):
        """Check if wearable integration is applicable for this class type"""
        # Generally applicable to most class types
        return True
```

### 5. Performance Monitoring Dashboard

```python
class PerformanceMonitoringDashboard:
    def __init__(self, db_connection, data_collector, analytics_engine):
        self.db = db_connection
        self.collector = data_collector
        self.analytics = analytics_engine
        self.active_dashboards = {}  # trainer_id -> list of active dashboard sessions
    
    def create_dashboard_session(self, trainer_id, class_id):
        """Create a new dashboard session for a trainer and class"""
        # Get class details
        class_details = self.db.get_class_details(class_id)
        if not class_details:
            return {"success": False, "reason": "Class not found"}
        
        # Check if collection is active
        try:
            snapshot = self.collector.get_real_time_snapshot(class_id)
            is_active = True
        except ValueError:
            # No active collection, start one
            collection_result = self.collector.start_class_collection(
                class_id, trainer_id, class_details["class_type"]
            )
            is_active = collection_result["success"]
            snapshot = self.collector.get_real_time_snapshot(class_id) if is_active else None
        
        if not is_active:
            return {"success": False, "reason": "Could not start data collection"}
        
        # Create dashboard session
        session_id = str(uuid.uuid4())
        dashboard_session = {
            "session_id": session_id,
            "trainer_id": trainer_id,
            "class_id": class_id,
            "class_details": class_details,
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "current_snapshot": snapshot
        }
        
        # Add to active dashboards
        if trainer_id not in self.active_dashboards:
            self.active_dashboards[trainer_id] = {}
        self.active_dashboards[trainer_id][session_id] = dashboard_session
        
        return {
            "success": True,
            "session_id": session_id,
            "dashboard_data": self._prepare_dashboard_data(dashboard_session)
        }
    
    def update_dashboard(self, trainer_id, session_id):
        """Update a dashboard with the latest data"""
        # Check if dashboard exists
        if trainer_id not in self.active_dashboards or session_id not in self.active_dashboards[trainer_id]:
            return {"success": False, "reason": "Dashboard session not found"}
        
        dashboard = self.active_dashboards[trainer_id][session_id]
        class_id = dashboard["class_id"]
        
        # Get latest snapshot
        try:
            snapshot = self.collector.get_real_time_snapshot(class_id)
        except ValueError:
            return {"success": False, "reason": "Data collection not active"}
        
        # Update dashboard
        dashboard["current_snapshot"] = snapshot
        dashboard["last_updated"] = datetime.now()
        
        return {
            "success": True,
            "dashboard_data": self._prepare_dashboard_data(dashboard)
        }
    
    def end_dashboard_session(self, trainer_id, session_id):
        """End a dashboard session"""
        # Check if dashboard exists
        if trainer_id not in self.active_dashboards or session_id not in self.active_dashboards[trainer_id]:
            return {"success": False, "reason": "Dashboard session not found"}
        
        dashboard = self.active_dashboards[trainer_id][session_id]
        class_id = dashboard["class_id"]
        
        # End data collection
        try:
            end_result = self.collector.end_class_collection(class_id)
        except ValueError:
            end_result = {"success": False, "reason": "Data collection not active"}
        
        # Remove dashboard
        del self.active_dashboards[trainer_id][session_id]
        if not self.active_dashboards[trainer_id]:
            del self.active_dashboards[trainer_id]
        
        return {
            "success": True,
            "collection_result": end_result
        }
    
    def get_active_dashboards(self, trainer_id):
        """Get all active dashboards for a trainer"""
        if trainer_id not in self.active_dashboards:
            return {"success": True, "dashboards": []}
        
        dashboards = []
        for session_id, dashboard in self.active_dashboards[trainer_id].items():
            dashboards.append({
                "session_id": session_id,
                "class_id": dashboard["class_id"],
                "class_name": dashboard["class_details"]["name"],
                "started_at": dashboard["created_at"].isoformat(),
                "last_updated": dashboard["last_updated"].isoformat()
            })
        
        return {"success": True, "dashboards": dashboards}
    
    def _prepare_dashboard_data(self, dashboard):
        """Prepare dashboard data for display"""
        snapshot = dashboard["current_snapshot"]
        class_details = dashboard["class_details"]
        
        # Basic dashboard data
        dashboard_data = {
            "session_id": dashboard["session_id"],
            "class_id": dashboard["class_id"],
            "class_name": class_details["name"],
            "class_type": class_details["class_type"],
            "start_time": class_details["start_time"],
            "duration_minutes": class_details["duration_minutes"],
            "last_updated": dashboard["last_updated"].isoformat(),
            "elapsed_minutes": (datetime.now() - datetime.fromisoformat(class_details["start_time"])).total_seconds() / 60 if "start_time" in class_details else 0
        }
        
        # Add metrics from snapshot
        if snapshot:
            dashboard_data.update({
                "active_members": snapshot["metrics"]["class_metrics"].get("active_members", 0),
                "attendance_rate": snapshot["metrics"]["class_metrics"].get("attendance_rate", 0),
                "class_metrics": snapshot["metrics"]["class_metrics"],
                "member_metrics": snapshot["metrics"]["member_metrics"],
                "insights": snapshot["insights"]
            })
        
        # Add historical context if available
        historical_context = self._get_historical_context(dashboard["class_id"], class_details["class_type"])
        if historical_context:
            dashboard_data["historical_context"] = historical_context
        
        return dashboard_data
    
    def _get_historical_context(self, class_id, class_type):
        """Get historical context for comparison"""
        # This would typically come from the analytics engine
        # For demonstration, return simulated data
        return {
            "avg_attendance_rate": 0.85,
            "avg_intensity_score": 7.2,
            "typical_member_count": 12
        }
```

## Frontend Implementation

### 1. Trainer Real-Time Dashboard

The real-time dashboard provides trainers with actionable insights during class sessions. Key components include:

- **Class Overview Panel**
  - Class name, type, and time remaining
  - Attendance metrics (expected vs. actual)
  - Overall class intensity metrics
  - Progress through planned workout segments

- **Member Grid**
  - Individual member cards with real-time metrics
  - Visual indicators for members needing attention
  - Quick access to member details and history
  - Ability to add notes or ratings for specific members

- **Insights Panel**
  - Real-time alerts and recommendations
  - Comparison to historical class performance
  - Suggested modifications based on current class dynamics

- **Timeline View**
  - Chronological view of class events and markers
  - Ability to add markers for key moments (e.g., "Started main workout")
  - Visual representation of intensity changes over time

- **Control Panel**
  - Start/stop data collection
  - Add class notes
  - Mark attendance
  - End class and view summary

### 2. Member Performance View

Members can access their own performance data through a dedicated interface:

- **Class History**
  - List of attended classes with performance metrics
  - Comparison to personal bests and averages
  - Progress tracking over time

- **Performance Details**
  - Detailed metrics for each class session
  - Visual representations of intensity, effort, and achievement
  - Trainer notes and feedback

- **Achievement Tracking**
  - Badges and rewards earned through performance
  - Progress toward goals
  - Comparison to peers (if enabled)

### 3. Admin Configuration Panel

Administrators can configure the performance monitoring system:

- **Data Source Management**
  - Enable/disable data sources
  - Configure integration parameters
  - Test connections

- **Metrics Configuration**
  - Define custom metrics and calculations
  - Set thresholds for alerts and insights
  - Configure default views for trainers

- **Class Type Settings**
  - Define which data sources apply to which class types
  - Set expected intensity ranges for different class types
  - Configure class-specific metrics

## Database Schema Updates

```sql
-- Performance Data Collection Sessions
CREATE TABLE performance_collection_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    trainer_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    status ENUM('active', 'completed', 'failed') NOT NULL DEFAULT 'active',
    active_sources JSON, -- List of active data source IDs
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (trainer_id) REFERENCES users(id)
);

-- Performance Collection Logs
CREATE TABLE performance_collection_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    collection_session_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- e.g., 'start', 'end', 'error'
    event_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_session_id) REFERENCES performance_collection_sessions(id)
);

-- Class Performance Data
CREATE TABLE class_performance_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    collection_session_id INT NOT NULL,
    performance_data JSON NOT NULL, -- Complete processed performance data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (collection_session_id) REFERENCES performance_collection_sessions(id)
);

-- Performance Summaries
CREATE TABLE performance_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    collection_session_id INT NOT NULL,
    summary_data JSON NOT NULL, -- Processed summary
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (collection_session_id) REFERENCES performance_collection_sessions(id)
);

-- Real-Time Insights
CREATE TABLE real_time_insights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    severity ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    insight_data JSON NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INT NULL,
    acknowledged_at TIMESTAMP NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (acknowledged_by) REFERENCES users(id)
);

-- Member Performance Records
CREATE TABLE member_performance_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    class_id INT NOT NULL,
    collection_session_id INT NOT NULL,
    performance_data JSON NOT NULL, -- Member-specific performance data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (collection_session_id) REFERENCES performance_collection_sessions(id)
);

-- Data Source Configurations
CREATE TABLE data_source_configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    configuration JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Class Type Data Source Mappings
CREATE TABLE class_type_data_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE KEY unique_class_source (class_type, source_id),
    FOREIGN KEY (source_id) REFERENCES data_source_configurations(source_id)
);
```

## Integration Points

### 1. Integration with Analytics Engine

The Performance Monitoring system integrates with the Analytics Engine to:

- Access historical performance data for comparison
- Feed collected data into predictive models
- Generate insights based on patterns and trends
- Calculate derived metrics and scores

```python
# Example integration with Analytics Engine
class PerformanceAnalyticsIntegration:
    def __init__(self, analytics_engine, performance_collector):
        self.analytics = analytics_engine
        self.collector = performance_collector
    
    def process_completed_class(self, class_id, performance_data):
        """Process performance data after class completion"""
        # Update member performance profiles
        self.analytics.update_member_performance_profiles(performance_data["member_data"])
        
        # Update class type performance metrics
        self.analytics.update_class_type_metrics(
            performance_data["class_type"],
            performance_data["aggregate_data"]
        )
        
        # Generate retention insights
        retention_insights = self.analytics.generate_retention_insights(
            performance_data["member_data"]
        )
        
        # Trigger automated communications if needed
        if retention_insights:
            for insight in retention_insights:
                if insight["type"] == "high_risk":
                    # Example: Trigger follow-up with high-risk members
                    self._trigger_retention_workflow(insight["member_id"])
    
    def _trigger_retention_workflow(self, member_id):
        """Trigger retention workflow for a member"""
        # This would integrate with the Automation Engine
        pass
```

### 2. Integration with Automation Engine

The Performance Monitoring system integrates with the Automation Engine to:

- Trigger automated communications based on performance insights
- Create follow-up tasks for trainers
- Schedule personalized workouts based on performance data
- Update member profiles and tags

```python
# Example integration with Automation Engine
class PerformanceAutomationIntegration:
    def __init__(self, automation_engine, performance_collector):
        self.automation = automation_engine
        self.collector = performance_collector
    
    def register_automation_triggers(self):
        """Register performance-based triggers with the automation engine"""
        triggers = [
            {
                "id": "high_performance_achievement",
                "description": "Member achieves exceptional performance",
                "handler": self._handle_high_performance
            },
            {
                "id": "low_engagement_detected",
                "description": "Member shows signs of low engagement during class",
                "handler": self._handle_low_engagement
            },
            {
                "id": "consistent_attendance",
                "description": "Member maintains consistent attendance",
                "handler": self._handle_consistent_attendance
            }
        ]
        
        for trigger in triggers:
            self.automation.register_trigger(trigger["id"], trigger["handler"])
    
    def _handle_high_performance(self, event_data):
        """Handle high performance achievement event"""
        member_id = event_data["member_id"]
        achievement = event_data["achievement"]
        
        # Example: Send congratulatory message
        self.automation.send_automated_message(
            member_id,
            "achievement_congratulation",
            {"achievement": achievement}
        )
        
        # Example: Add achievement badge
        self.automation.add_member_badge(
            member_id,
            achievement["badge_type"],
            {"source": "performance_monitoring", "details": achievement}
        )
    
    # Additional handler methods for other triggers
```

### 3. Integration with Trainer Tools

The Performance Monitoring system integrates with the AI Trainer Tools to:

- Provide real-time data for workout adjustments
- Feed performance data into workout planning algorithms
- Enhance scheduling based on class performance patterns
- Support personalized member guidance

```python
# Example integration with AI Trainer Tools
class PerformanceTrainerToolsIntegration:
    def __init__(self, trainer_tools, performance_collector):
        self.trainer_tools = trainer_tools
        self.collector = performance_collector
    
    def enhance_workout_planning(self, member_id, plan_request):
        """Enhance workout planning with performance data"""
        # Get recent performance data
        recent_performance = self._get_recent_performance(member_id)
        
        # Enhance plan request with performance insights
        enhanced_request = plan_request.copy()
        enhanced_request["performance_context"] = {
            "recent_intensity_levels": recent_performance.get("intensity_levels", []),
            "exercise_proficiency": recent_performance.get("exercise_proficiency", {}),
            "recovery_indicators": recent_performance.get("recovery_indicators", {})
        }
        
        # Generate enhanced plan
        return self.trainer_tools.generate_workout_plan(member_id, enhanced_request)
    
    def _get_recent_performance(self, member_id):
        """Get recent performance data for a member"""
        # This would typically query the database for recent performance records
        # For demonstration, return simulated data
        return {
            "intensity_levels": [7.2, 8.1, 6.5, 7.8],  # Last 4 classes
            "exercise_proficiency": {
                "squat": 0.85,
                "pushup": 0.92,
                "lunge": 0.78
            },
            "recovery_indicators": {
                "avg_recovery_heart_rate": 95,
                "recovery_time_minutes": 12
            }
        }
```

## Next Steps

1. **Implement Core Components**
   - Develop the `PerformanceDataCollector` and `DataSourcesManager` classes
   - Implement the built-in data sources (manual tracking, app check-in, trainer input)
   - Create the database schema for performance data storage

2. **Develop Frontend Components**
   - Build the real-time trainer dashboard interface
   - Implement the member performance view
   - Create the admin configuration panel

3. **Integrate with Existing Systems**
   - Connect with the Analytics Engine for historical context and insights
   - Integrate with the Automation Engine for triggered workflows
   - Link with AI Trainer Tools for enhanced workout planning

4. **Test and Validate**
   - Test with simulated data streams
   - Validate accuracy of derived metrics and insights
   - Ensure real-time performance meets requirements

5. **Prepare for Hardware Integration**
   - Document APIs for external data source integration
   - Create sample implementations for common wearables
   - Develop testing tools for new data source validation

6. **Documentation and Training**
   - Create user guides for trainers and administrators
   - Develop technical documentation for future extensions
   - Prepare training materials for effective system use
