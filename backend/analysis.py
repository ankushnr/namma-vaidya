def compute_risk(age, symptoms, history, duration, spo2_str):
    score = 0
    sym = symptoms.lower()

    # Age factor
    if age > 65:   score += 30
    elif age > 45: score += 18
    elif age > 30: score += 8
    else:          score += 3

    # High-risk symptom keywords
    high_risk = ['chest pain','chest','breathless','shortness of breath',
                 'unconscious','seizure','stroke','paralysis','severe headache','blood']
    med_risk  = ['fever','fatigue','vomiting','dizziness','nausea',
                 'pain','cough','swelling','pressure']

    for w in high_risk:
        if w in sym: score += 20
    for w in med_risk:
        if w in sym: score += 8

    # Medical history
    multi     = ['multiple conditions']
    high_hist = ['diabetes','hypertension','heart disease']
    med_hist  = ['asthma / copd', 'asthma']

    h = history.lower()
    if any(x in h for x in multi):      score += 20
    elif any(x in h for x in high_hist): score += 15
    elif any(x in h for x in med_hist):  score += 10

    # Duration
    dur = duration.lower()
    if 'month'  in dur: score += 15
    elif 'week' in dur: score += 10
    elif '4–7'  in dur: score += 6
    elif '4-7'  in dur: score += 6

    # SpO2
    try:
        spo2 = int(''.join(filter(str.isdigit, spo2_str)))
        if spo2 < 94: score += 20
    except:
        pass

    score = min(score, 98)

    if score >= 65:
        return {
            'risk_score': score, 'risk_level': 'High',
            'condition_class': 'Ce-3', 'severity_level': 'L3', 'grade': 'G-Critical',
            'treatments': [
                'Immediate hospital admission and continuous monitoring.',
                'Start oxygen therapy if SpO₂ below 94%.',
                'IV access and fluid resuscitation as required.',
                'Urgent specialist referral (cardiology / pulmonology).',
                'ECG, CBC, BMP blood work — STAT.',
                'Initiate emergency protocol if needed.'
            ],
            'tags': ['Urgent Review','Hospitalisation','Specialist Referral','High Priority']
        }
    elif score >= 35:
        return {
            'risk_score': score, 'risk_level': 'Moderate',
            'condition_class': 'Ce-2', 'severity_level': 'L2', 'grade': 'G-Moderate',
            'treatments': [
                'Schedule clinic follow-up within 24–48 hours.',
                'Prescribe symptomatic relief medications.',
                'Monitor vitals every 4–6 hours if managing at home.',
                'Order blood tests and imaging if symptoms worsen.',
                'Advise rest and maintain hydration.',
                'Review and adjust chronic condition medications.'
            ],
            'tags': ['Follow-up Required','Medication Review','Monitor at Home','Moderate Priority']
        }
    else:
        return {
            'risk_score': score, 'risk_level': 'Low',
            'condition_class': 'Ce-1', 'severity_level': 'L1', 'grade': 'G-Mild',
            'treatments': [
                'Outpatient management is appropriate.',
                'Symptomatic treatment — rest, fluids, OTC medication.',
                'Routine follow-up in 5–7 days if symptoms persist.',
                'Advise healthy diet and adequate sleep.',
                'No urgent investigations needed.',
                'Return if symptoms escalate or new symptoms develop.'
            ],
            'tags': ['Outpatient Care','Self-Management','Routine Follow-up','Low Priority']
        }