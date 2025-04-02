from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import numpy as np
from scipy.stats import norm
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.secret_key = 'IamWainaina@2002'

    @app.route('/', methods=['GET', 'POST'])
    def index():
        print("Index route accessed")
        if request.method == 'POST':
            session['name'] = request.form.get('name')
            session['email'] = request.form.get('email')
            session['phone'] = request.form.get('phone')
            print(f"Form Data: {session['name']}, {session['email']}, {session['phone']}")
            return redirect(url_for('assessment'))
        return render_template('index.html')

    @app.route('/assessment', methods=['GET', 'POST'])
    def assessment():
        print("Assessment route accessed")
        if request.method == 'POST':
            session['assessment_data'] = request.form
            return redirect(url_for('results'))
        return render_template('assessment.html')

    class EnergyInferenceEngine:
        def __init__(self):
            # This is the database file where we store all our home energy data
            self.db_path = 'home_energy.sql'
            
            # These numbers help us group houses by their size
            # Example: a house smaller than 500 sq ft is 'very_small'
            self.size_thresholds = {
                'very_small': 500,   # Like a small apartment
                'small': 1000,       # Like a normal apartment
                'medium': 2000,      # Like a normal house
                'large': 3000,       # Like a big house
                'very_large': 4000   # Like a mansion
            }
            
            # These numbers help us understand how much people use their appliances
            # Numbers are in hours per day
            self.usage_thresholds = {
                'very_low': 3,      # Using appliances for 3 hours or less
                'low': 6,           # Using appliances for 6 hours
                'medium': 12,       # Using appliances for half a day
                'high': 18,         # Using appliances most of the day
                'very_high': 24     # Using appliances all day
            }
            
            # If something goes wrong, we'll use these basic tips
            # These are always helpful for everyone
            self.default_recommendations = [
                "Install LED bulbs for better energy efficiency",  # LED bulbs use less power
                "Use natural light when possible",                 # Sunlight is free!
                "Unplug devices when not in use",                 # Even off devices use some power
                "Regular maintenance of HVAC systems",            # Clean systems work better
                "Consider using smart power strips"               # These turn off power automatically
            ]
            
            # These numbers help us understand if a room is too hot or too cold
            # Temperature is in Celsius
            self.temp_params = {
                'cold': (16, 20),    # Below 20°C might need heating
                'comfort': (20, 24),  # Most people like this range
                'hot': (24, 30)      # Above 24°C might need cooling
            }
            
            # This number helps us guess if someone uses too much power
            # 0.3 means we think 30% of homes use too much power
            self.appliance_high_usage_prior = 0.3
            
        def validate_assessment_data(self, assessment_data):
            """
            Make sure the numbers users give us make sense.
            If they type words instead of numbers, we'll use default values.
            """
            try:
                return {
                    'homeSize': float(assessment_data.get('homeSize', 1000)),
                    'occupants': int(assessment_data.get('occupants', 1)),
                    'location': str(assessment_data.get('location', '')),
                    'homeType': str(assessment_data.get('homeType', '')),
                    'acHours': float(assessment_data.get('acHours', 0)),
                    'preferredTemp': float(assessment_data.get('preferredTemp', 23))
                }
            except (ValueError, TypeError):
                return None

        def get_similar_homes(self, size, occupants, location, home_type):
            """
            Find homes in our database that are similar to the user's home.
            We look for homes that are:
            1. About the same size (within 500 sq ft)
            2. Have similar number of people (within 2 people)
            3. In the same location
            4. Same type of home (apartment, house, etc.)
            
            If we can't find exact matches, we'll look for homes that are
            just similar in size.
            """
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Try exact match first
                cursor.execute("""
                    SELECT h.id, h.size, h.occupants, b.peak_usage_hours, b.daily_usage_hours
                    FROM home h
                    JOIN behavior b ON h.id = b.home_id
                    WHERE h.home_type = ? AND h.location = ?
                    AND ABS(h.size - ?) <= 500
                    AND ABS(h.occupants - ?) <= 2
                """, (home_type, location, size, occupants))
                
                similar_homes = cursor.fetchall()
                
                # If no matches, try with relaxed criteria
                if not similar_homes:
                    cursor.execute("""
                        SELECT h.id, h.size, h.occupants, b.peak_usage_hours, b.daily_usage_hours
                        FROM home h
                        JOIN behavior b ON h.id = b.home_id
                        WHERE ABS(h.size - ?) <= 1000
                        LIMIT 5
                    """, (size,))
                    similar_homes = cursor.fetchall()
                
                conn.close()
                return similar_homes
            except sqlite3.Error:
                return []

        def apply_rule_based_logic(self, assessment_data):
            rules = []
            
            # Size-based rules
            size = float(assessment_data.get('homeSize', 0))
            if size < self.size_thresholds['small']:
                rules.append("Consider using space-efficient appliances")
            elif size > self.size_thresholds['large']:
                rules.append("Implement zone-based heating/cooling")
            
            # Usage pattern rules
            ac_hours = float(assessment_data.get('acHours', 0))
            if ac_hours > self.usage_thresholds['high']:
                rules.append("High AC usage detected. Consider programmable thermostat")
            
            return rules
        
        def apply_fuzzy_logic(self, assessment_data):
            recommendations = []
            
            # Temperature comfort fuzzy logic
            temp = float(assessment_data.get('preferredTemp', 23))
            
            # Calculate membership degrees
            cold_degree = max(0, min(1, (self.temp_params['cold'][1] - temp) / 
                                      (self.temp_params['cold'][1] - self.temp_params['cold'][0])))
            hot_degree = max(0, min(1, (temp - self.temp_params['hot'][0]) / 
                                      (self.temp_params['hot'][1] - self.temp_params['hot'][0])))
            comfort_degree = max(0, min(1, 1 - cold_degree - hot_degree))
            
            if cold_degree > 0.6:
                recommendations.append("Temperature settings suggest high heating needs")
            elif hot_degree > 0.6:
                recommendations.append("Consider natural cooling methods")
                
            return recommendations
        
        def apply_bayesian_reasoning(self, assessment_data, similar_homes):
            insights = []
            
            # Calculate likelihood of high energy usage based on similar homes
            if similar_homes:
                high_usage_count = sum(1 for home in similar_homes if home[4] > self.usage_thresholds['high'])
                likelihood = high_usage_count / len(similar_homes)
                
                # Bayes theorem
                posterior = (likelihood * self.appliance_high_usage_prior) / (
                    (likelihood * self.appliance_high_usage_prior) + 
                    ((1 - likelihood) * (1 - self.appliance_high_usage_prior))
                )
                
                if posterior > 0.7:
                    insights.append("High probability of excessive energy usage compared to similar homes")
                elif posterior < 0.3:
                    insights.append("Your usage pattern is more efficient than similar homes")
                    
            return insights
        
        def get_recommendations(self, assessment_data):
            """
            Create a list of energy-saving tips for the user.
            We'll always give at least 3 tips, even if something goes wrong.
            
            Here's what we do:
            1. Check if the user's data makes sense
            2. Look for similar homes
            3. Compare their energy use with others
            4. Give specific tips based on their home
            5. Add general tips if we need more
            """
            recommendations = set()  # Use set to avoid duplicates
            
            # Validate input data
            validated_data = self.validate_assessment_data(assessment_data)
            if not validated_data:
                return self.default_recommendations[:3]  # Return top 3 default recommendations
            
            # Get similar homes
            similar_homes = self.get_similar_homes(
                validated_data['homeSize'],
                validated_data['occupants'],
                validated_data['location'],
                validated_data['homeType']
            )
            
            # Apply different reasoning methods with error handling
            try:
                rule_based = self.apply_rule_based_logic(validated_data)
                recommendations.update(rule_based)
            except Exception:
                recommendations.add(self.default_recommendations[0])
                
            try:
                fuzzy_logic = self.apply_fuzzy_logic(validated_data)
                recommendations.update(fuzzy_logic)
            except Exception:
                recommendations.add(self.default_recommendations[1])
                
            try:
                bayesian = self.apply_bayesian_reasoning(validated_data, similar_homes)
                recommendations.update(bayesian)
            except Exception:
                recommendations.add(self.default_recommendations[2])
            
            # Ensure minimum number of recommendations
            recommendations_list = list(recommendations)
            while len(recommendations_list) < 3:
                for rec in self.default_recommendations:
                    if rec not in recommendations_list:
                        recommendations_list.append(rec)
                        break
            
            return recommendations_list[:5]  # Return top 5 recommendations

    @app.route('/results')
    def results():
        print("Results route accessed")
        if 'assessment_data' not in session:
            return redirect(url_for('index'))
            
        engine = EnergyInferenceEngine()
        recommendations = engine.get_recommendations(session['assessment_data'])
        
        return render_template('results.html', 
                             recommendations=recommendations,
                             assessment_data=session['assessment_data'],
                             date=datetime.now().strftime('%B %d, %Y'))

    return app

app = create_app()

if __name__ == '__main__':
    print("Running Flask App...")
    app.run(debug=True)
