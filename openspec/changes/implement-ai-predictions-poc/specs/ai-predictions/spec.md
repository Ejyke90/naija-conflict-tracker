# AI Predictions Capability

## ADDED Requirements

### Requirement: Next 30-Day Conflict Predictions API
The system SHALL provide an API endpoint that returns AI-powered conflict predictions for the next 30 days for the top 5 at-risk Nigerian states, including predicted incidents, predicted fatalities, confidence intervals, and accuracy metrics.

#### Scenario: User views next 30-day predictions for Borno
Given the user is on the dashboard Analytics tab
When they view the AI Predictions section
Then they see a prediction card for Borno showing:
- Predicted incidents for next 30 days: 42 (CI: 35-49)
- Predicted fatalities for next 30 days: 156 (CI: 120-195)
- Risk level: CRITICAL
- Model accuracy: 82% (MAPE)

#### Scenario: Predictions update every 6 hours
Given the user is viewing the AI Predictions section
When 6 hours have passed since the last prediction fetch
Then the component automatically refreshes predictions from the API
And displays "Last updated: 6 hours ago" timestamp
And user can click "Refresh" button for manual update

#### Scenario: Predictions include confidence intervals
Given the user is viewing a conflict prediction
When they look at the predicted values
Then they see both point estimate and 90% confidence interval
And can understand the range of possible outcomes
Example: "Predicted 42 incidents (35-49)"

### Requirement: Risk Level Classification for Predictions
The system SHALL classify each state's predicted conflict risk into levels (Low, Medium, High, Critical) based on predicted incident rate and severity.

#### Scenario: Borno classified as Critical risk
Given the top 5 at-risk states have been identified
When Borno has predicted incident rate > 1 per day
Then it is classified as CRITICAL risk level
And displayed with red color badge

#### Scenario: Lagos classified as Low risk
Given Lagos has predicted incident rate < 0.1 per day
When the risk classification is calculated
Then it is classified as LOW risk level
And displayed with green color badge

### Requirement: Prediction Accuracy Metrics
The system SHALL display model accuracy metrics (MAPE) and model type for each prediction to set user expectations about forecast reliability.

#### Scenario: Accuracy metric shown in prediction card
Given a conflict prediction is displayed
When the user views the prediction card
Then they see "Accuracy: 82% (MAPE)" or similar metric
And can understand how reliable this prediction is
And see which model was used (Ensemble, Prophet, ARIMA)

#### Scenario: Last training date disclosed
Given the user wants to know if predictions are stale
When they view a prediction card
Then they see "Last trained: 2 hours ago"
And can assess if the model was recently updated with latest data