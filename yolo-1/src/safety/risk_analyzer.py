import torch
import numpy as np

class RiskAnalyzer:
    def __init__(self, risk_model, thresholds):
        self.risk_model = risk_model
        self.thresholds = thresholds

    def analyze_risk(self, vehicle_data):
        """
        Analyzes the risk level based on vehicle data and predictions.
        
        Parameters:
            vehicle_data (dict): A dictionary containing vehicle data such as speed, headway, and visibility.
        
        Returns:
            str: The risk level as a string.
        """
        vsv = vehicle_data.get('vsv', 0.0)
        vlv = vehicle_data.get('vlv', 0.0)
        headway = vehicle_data.get('headway', 0.0)
        visibility = vehicle_data.get('visibility', 'sunny')

        # Prepare input for the risk model
        input_data = torch.tensor([[vsv, vlv, headway]], dtype=torch.float32)
        with torch.no_grad():
            risk_prediction = self.risk_model(input_data).squeeze().numpy()

        max_risk = max(risk_prediction)

        if max_risk > self.thresholds[0]:
            return "critical"
        elif max_risk > self.thresholds[1]:
            return "high"
        elif max_risk > self.thresholds[2]:
            return "moderate"
        else:
            return "low"