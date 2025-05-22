# Member Challenges and Competitions Implementation

## Overview

This document outlines the implementation approach for the member challenges and competitions feature for the Training Club Fitness Platform. This feature aims to enhance member engagement and motivation through structured competitive and collaborative activities, integrated seamlessly with the existing gamification and social systems. Automation is a key principle in the design to minimize administrative overhead.

## Core Components

### 1. Challenge & Competition Engine

```python
class ChallengeCompetitionEngine:
    def __init__(self, db_connection, notification_service, gamification_engine):
        self.db = db_connection
        self.notification_service = notification_service
        self.gamification_engine = gamification_engine
        self.challenge_templates = self._load_challenge_templates()
        self.scheduler = BackgroundScheduler()
    
    def start_automation(self):
        """Start automated challenge management jobs"""
        # Schedule automated challenge creation
        self.scheduler.add_job(
            self._create_automated_challenges,
            'cron',
            day_of_week='sun', # Create weekly challenges on Sunday
            hour=2
        )
        
        # Schedule challenge status updates (start/end)
        self.scheduler.add_job(
            self._update_challenge_statuses,
            'interval',
            minutes=15
        )
        
        # Schedule result calculation and reward distribution
        self.scheduler.add_job(
            self._process_completed_challenges,
            'interval',
            minutes=30
        )
        
        self.scheduler.start()

    def create_challenge(self, admin_id, challenge_data):
        """Create a new challenge or competition (manual)"""
        # Validate admin permissions
        if not is_admin(admin_id):
            return {"success": False, "reason": "Unauthorized"}
        
        # Validate challenge data
        validation = self._validate_challenge_data(challenge_data)
        if not validation["valid"]:
            return {"success": False, "reason": validation["reason"]}
        
        # Create challenge in database
        challenge_id = self.db.create_challenge(challenge_data)
        
        # Notify relevant users about the new challenge (optional)
        # self._notify_new_challenge(challenge_id, challenge_data)
        
        return {"success": True, "challenge_id": challenge_id}

    def get_available_challenges(self, user_id, filter_options=None, page=1, page_size=10):
        """Get list of available challenges for a user"""
        challenges = self.db.get_available_challenges(user_id, filter_options, page, page_size)
        enriched_challenges = self._enrich_challenge_data(challenges, user_id)
        return {
            "challenges": enriched_challenges,
            "page": page,
            "page_size": page_size,
            "has_more": len(challenges) == page_size
        }

    def get_challenge_details(self, user_id, challenge_id):
        """Get detailed information about a specific challenge"""
        details = self.db.get_challenge_details(challenge_id)
        if not details:
            return {"success": False, "reason": "Challenge not found"}
        
        # Enrich with user-specific data (participation status, progress)
        enriched_details = self._enrich_challenge_details(details, user_id)
        return {"success": True, "details": enriched_details}

    def join_challenge(self, user_id, challenge_id, team_id=None):
        """Allow a user to join a challenge"""
        # Validate eligibility
        eligibility = self._check_challenge_eligibility(user_id, challenge_id)
        if not eligibility["eligible"]:
            return {"success": False, "reason": eligibility["reason"]}
        
        # Process joining
        result = self.db.add_challenge_participant(user_id, challenge_id, team_id)
        if result["success"]:
            # Update gamification (e.g., points for joining)
            self.gamification_engine.process_activity(
                user_id, 
                'challenge_joined',
                {'challenge_id': challenge_id}
            )
            self.notification_service.notify_challenge_joined(user_id, challenge_id)
        return result

    def leave_challenge(self, user_id, challenge_id):
        """Allow a user to leave a challenge"""
        result = self.db.remove_challenge_participant(user_id, challenge_id)
        if result["success"]:
            self.notification_service.notify_challenge_left(user_id, challenge_id)
        return result

    def update_challenge_progress(self, user_id, challenge_id, activity_type, activity_data):
        """Update user's progress in a challenge based on tracked activity"""
        # Check if user is participating
        if not self.db.is_user_participating(user_id, challenge_id):
            return # Not participating
        
        # Get challenge details and tracking metric
        challenge = self.db.get_challenge_details(challenge_id)
        if not challenge or challenge['status'] != 'active':
            return # Challenge not active or found
            
        tracking_metric = challenge['tracking_metric']
        
        # Calculate progress increment based on activity
        progress_increment = self._calculate_progress_increment(
            activity_type, 
            activity_data, 
            tracking_metric
        )
        
        if progress_increment > 0:
            # Update progress in database
            new_progress = self.db.update_participant_progress(
                user_id, 
                challenge_id, 
                progress_increment
            )
            
            # Check if challenge goal is met
            if new_progress >= challenge['goal']:
                 # Potentially trigger immediate reward or notification
                 self._process_individual_goal_met(user_id, challenge_id)

            # Update gamification (e.g., points for progress)
            self.gamification_engine.process_activity(
                user_id, 
                'challenge_progress',
                {'challenge_id': challenge_id, 'progress': progress_increment}
            )

    def get_challenge_leaderboard(self, challenge_id, user_id=None, page=1, page_size=20):
        """Get the leaderboard for a specific challenge"""
        leaderboard_data = self.db.get_challenge_leaderboard(challenge_id, page, page_size)
        user_rank = None
        if user_id:
             user_rank = self.db.get_user_challenge_rank(user_id, challenge_id)
             
        enriched_leaderboard = self._enrich_leaderboard_data(leaderboard_data, user_id)
        return {
            "leaderboard": enriched_leaderboard,
            "user_rank": user_rank,
            "page": page,
            "page_size": page_size,
            "has_more": len(leaderboard_data) == page_size
        }

    # --- Automation Methods ---
    def _create_automated_challenges(self):
        """Automatically create challenges based on templates"""
        for template in self.challenge_templates:
            if self._should_create_challenge_from_template(template):
                challenge_data = self._generate_challenge_data_from_template(template)
                self.db.create_challenge(challenge_data)
                # Optionally notify users

    def _update_challenge_statuses(self):
        """Update challenge statuses (pending -> active, active -> completed)"""
        now = datetime.now()
        # Start pending challenges
        pending_challenges = self.db.get_challenges_by_status('pending')
        for challenge in pending_challenges:
            if challenge['start_date'] <= now:
                self.db.update_challenge_status(challenge['id'], 'active')
                self.notification_service.notify_challenge_started(challenge['id'])
        
        # End active challenges
        active_challenges = self.db.get_challenges_by_status('active')
        for challenge in active_challenges:
            if challenge['end_date'] <= now:
                self.db.update_challenge_status(challenge['id'], 'calculating') # Status before completed

    def _process_completed_challenges(self):
        """Calculate results and distribute rewards for completed challenges"""
        challenges_to_process = self.db.get_challenges_by_status('calculating')
        for challenge in challenges_to_process:
            # Calculate final rankings/results
            results = self._calculate_challenge_results(challenge['id'])
            self.db.store_challenge_results(challenge['id'], results)
            
            # Distribute rewards based on results
            self._distribute_challenge_rewards(challenge, results)
            
            # Update status to completed
            self.db.update_challenge_status(challenge['id'], 'completed')
            self.notification_service.notify_challenge_completed(challenge['id'], results)

    # --- Helper Methods ---
    def _load_challenge_templates(self):
        """Load challenge templates from config or database"""
        # Implementation details
        return [] 

    def _validate_challenge_data(self, data):
        """Validate data for creating a new challenge"""
        # Implementation details
        return {"valid": True}

    def _enrich_challenge_data(self, challenges, user_id):
        """Add user-specific info (participation status) to challenge list"""
        # Implementation details
        return challenges
        
    def _enrich_challenge_details(self, details, user_id):
        """Add user participation status and progress to challenge details"""
        # Implementation details
        return details

    def _check_challenge_eligibility(self, user_id, challenge_id):
        """Check if user is eligible to join the challenge"""
        # Implementation details (check level, membership, previous participation etc.)
        return {"eligible": True}

    def _calculate_progress_increment(self, activity_type, activity_data, tracking_metric):
        """Calculate progress increment based on activity and metric"""
        # Example: if tracking_metric is 'distance_km' and activity is 'run', return activity_data['distance']
        # Implementation details
        return 0
        
    def _process_individual_goal_met(self, user_id, challenge_id):
        """Handle logic when an individual meets the challenge goal before the end date"""
        # E.g., award bonus points, send notification
        pass

    def _enrich_leaderboard_data(self, leaderboard, user_id):
        """Add extra info to leaderboard entries"""
        # Implementation details
        return leaderboard
        
    def _should_create_challenge_from_template(self, template):
        """Determine if a challenge should be created based on template rules"""
        # Implementation details (check frequency, conditions)
        return False
        
    def _generate_challenge_data_from_template(self, template):
        """Generate specific challenge data from a template"""
        # Implementation details (set dates, goals based on template)
        return {}
        
    def _calculate_challenge_results(self, challenge_id):
        """Calculate final rankings and results for a completed challenge"""
        # Implementation details (get final progress, determine winners)
        return {}
        
    def _distribute_challenge_rewards(self, challenge, results):
        """Distribute gamification points/rewards based on challenge results"""
        # Implementation details (iterate through winners/participants, call gamification_engine)
        pass
```

## Frontend Implementation

### 1. Challenges List Component

```typescript
// React component to display available challenges
import React, { useState, useEffect, useCallback } from 'react';
import { challengeService } from '../services';
import { ChallengeCard, LoadingSpinner, FilterControls } from '../components';

const ChallengesList: React.FC = () => {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [filters, setFilters] = useState({}); // e.g., { type: 'individual', status: 'active' }

  const loadChallenges = useCallback(async (reset = false) => {
    const pageToLoad = reset ? 1 : page;
    if (reset) {
      setLoading(true);
      setPage(1);
    }
    
    try {
      const data = await challengeService.getAvailableChallenges(filters, pageToLoad);
      if (reset || pageToLoad === 1) {
        setChallenges(data.challenges);
      } else {
        setChallenges(prev => [...prev, ...data.challenges]);
      }
      setHasMore(data.has_more);
      setPage(pageToLoad + 1);
    } catch (error) {
      console.error('Error loading challenges:', error);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    loadChallenges(true);
  }, [filters, loadChallenges]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="challenges-list-container">
      <h1>Challenges & Competitions</h1>
      <FilterControls options={['type', 'status']} onChange={handleFilterChange} />
      
      {loading && page === 1 && <LoadingSpinner />}
      
      <div className="challenges-grid">
        {challenges.map(challenge => (
          <ChallengeCard key={challenge.id} challenge={challenge} />
        ))}
      </div>
      
      {challenges.length === 0 && !loading && (
        <p>No challenges match your criteria. Check back later!</p>
      )}
      
      {hasMore && (
        <button onClick={() => loadChallenges(false)} disabled={loading}>
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
};

export default ChallengesList;
```

### 2. Challenge Details Component

```typescript
// React component for viewing challenge details
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { challengeService } from '../services';
import { LoadingSpinner, ChallengeInfo, ParticipantList, ChallengeLeaderboard, JoinButton } from '../components';
import { useAuth } from '../contexts/AuthContext';

const ChallengeDetails: React.FC = () => {
  const { challengeId } = useParams();
  const { currentUser } = useAuth();
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await challengeService.getChallengeDetails(challengeId);
        if (data.success) {
          setDetails(data.details);
        } else {
          setError(data.reason);
        }
      } catch (err) {
        setError('Failed to load challenge details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [challengeId]);

  const handleJoin = async () => {
    try {
      const result = await challengeService.joinChallenge(challengeId);
      if (result.success) {
        // Update participation status locally
        setDetails(prev => ({ ...prev, user_participation: { status: 'joined', progress: 0 } }));
      } else {
        alert(`Failed to join: ${result.reason}`);
      }
    } catch (err) {
      alert('An error occurred while trying to join.');
      console.error(err);
    }
  };
  
  const handleLeave = async () => {
     // Similar logic for leaving
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;
  if (!details) return <div>Challenge not found.</div>;

  return (
    <div className="challenge-details-container">
      <ChallengeInfo details={details} />
      
      {details.status === 'active' && !details.user_participation && (
        <JoinButton onJoin={handleJoin} eligibility={details.user_eligibility} />
      )}
      {details.user_participation?.status === 'joined' && details.status === 'active' && (
         <button onClick={handleLeave}>Leave Challenge</button>
      )}
      
      {/* Display progress if participating */} 
      {details.user_participation && (
          <div>Your Progress: {details.user_participation.progress} / {details.goal} {details.tracking_unit}</div>
      )}

      {/* Leaderboard or Participant List based on challenge type */} 
      {details.type === 'competition' ? (
        <ChallengeLeaderboard challengeId={challengeId} />
      ) : (
        <ParticipantList challengeId={challengeId} />
      )}
    </div>
  );
};

export default ChallengeDetails;
```

## Backend API Endpoints

```python
@app.route('/api/challenges', methods=['GET'])
@jwt_required
def get_challenges():
    user_id = get_jwt_identity()
    filters = request.args.to_dict()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.get_available_challenges(user_id, filters, page, page_size)
    return jsonify(result)

@app.route('/api/challenges/<challenge_id>', methods=['GET'])
@jwt_required
def get_challenge(challenge_id):
    user_id = get_jwt_identity()
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.get_challenge_details(user_id, challenge_id)
    if not result['success']:
        return jsonify({'error': result['reason']}), 404
    return jsonify(result['details'])

@app.route('/api/challenges/<challenge_id>/join', methods=['POST'])
@jwt_required
def join_challenge_route(challenge_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    team_id = data.get('team_id')
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.join_challenge(user_id, challenge_id, team_id)
    if not result['success']:
        return jsonify({'error': result['reason']}), 400
    return jsonify(result)

@app.route('/api/challenges/<challenge_id>/leave', methods=['POST'])
@jwt_required
def leave_challenge_route(challenge_id):
    user_id = get_jwt_identity()
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.leave_challenge(user_id, challenge_id)
    if not result['success']:
        return jsonify({'error': result['reason']}), 400
    return jsonify(result)

@app.route('/api/challenges/<challenge_id>/leaderboard', methods=['GET'])
@jwt_required
def get_challenge_leaderboard_route(challenge_id):
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.get_challenge_leaderboard(challenge_id, user_id, page, page_size)
    return jsonify(result)

# Admin endpoint to create challenges
@app.route('/api/admin/challenges', methods=['POST'])
@jwt_required
@admin_required # Decorator to check admin role
def create_challenge_admin():
    admin_id = get_jwt_identity()
    challenge_data = request.get_json()
    if not challenge_data:
        return jsonify({'error': 'Request body required'}), 400
    engine = ChallengeCompetitionEngine(db, notification_service, gamification_engine)
    result = engine.create_challenge(admin_id, challenge_data)
    if not result['success']:
        return jsonify({'error': result['reason']}), 400
    return jsonify(result), 201
```

## Database Schema Updates

```sql
CREATE TABLE challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    type ENUM('individual', 'team', 'community') NOT NULL,
    status ENUM('pending', 'active', 'calculating', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    tracking_metric VARCHAR(50) NOT NULL, -- e.g., 'distance_km', 'calories_burned', 'workouts_completed'
    tracking_unit VARCHAR(20),
    goal DECIMAL(10, 2),
    rules JSON, -- Eligibility rules, participation limits, etc.
    reward_config JSON, -- How rewards are distributed (e.g., top 3, all finishers)
    created_by INT, -- Admin user ID or NULL for automated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE challenge_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    user_id INT NOT NULL,
    team_id INT NULL, -- For team challenges
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress DECIMAL(10, 2) NOT NULL DEFAULT 0,
    last_progress_update TIMESTAMP NULL,
    status ENUM('active', 'withdrawn', 'completed') NOT NULL DEFAULT 'active',
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    -- FOREIGN KEY (team_id) REFERENCES challenge_teams(id), -- If using a teams table
    UNIQUE KEY unique_participant (challenge_id, user_id)
);

CREATE TABLE challenge_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    user_id INT NOT NULL,
    rank INT,
    final_progress DECIMAL(10, 2),
    rewards_distributed JSON,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_result (challenge_id, user_id)
);

-- Optional: Table for teams in team challenges
-- CREATE TABLE challenge_teams (...);

-- Indexes
CREATE INDEX idx_challenges_status_dates ON challenges(status, start_date, end_date);
CREATE INDEX idx_challenge_participants_challenge ON challenge_participants(challenge_id);
CREATE INDEX idx_challenge_participants_user ON challenge_participants(user_id);
CREATE INDEX idx_challenge_results_challenge ON challenge_results(challenge_id);
```

## Integration with Automation Framework

- The `AutomatedActivityTracker` needs to be updated to call `ChallengeCompetitionEngine.update_challenge_progress` when relevant activities are tracked.
- The `ChallengeCompetitionEngine` includes scheduled tasks (`_create_automated_challenges`, `_update_challenge_statuses`, `_process_completed_challenges`) managed by `apscheduler` or a similar library, started via `start_automation()`.
- Notifications for challenge events (start, end, join, leave, results) are handled by the `NotificationService`.
- Rewards are distributed by calling the `GamificationEngine`.

## Next Steps

1. Implement the `ChallengeCompetitionEngine` backend logic.
2. Update the database schema.
3. Develop the required API endpoints.
4. Create the frontend components (`ChallengesList`, `ChallengeDetails`, etc.).
5. Integrate challenge progress updates into the `AutomatedActivityTracker`.
6. Implement and test the automated challenge management tasks.
7. Thoroughly test the entire feature flow.
