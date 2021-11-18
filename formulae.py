from math import log

abnormalities = ["High Anion Gap Metabolic Acidosis", "Normal Anion Gap Metabolic Acidosis",
                 "Low Anion Gap Metabolic Acidosis",
                 "Metabolic Alkalosis", "Acute Respiratory Acidosis", "Chronic Respiratory Acidosis",
                 "Acute respiratory Alkalosis", "Chronic Respiratory Alkalosis"]

deliverytypes =["Nasal Canula", "Face Mask", "NRBM", "Venturi Mask"]
venturicolorcodes =["Blue", "White", "Orange", "Yellow", "Red", "Green"]

def calculatedph(pco2, hco3):
    h = 24 * pco2 / hco3
    #ph = 7.4 + (40 - h) * 0.01
    ph = -log(h / 1000000000, 10)
    print("caclucalted ph:", ph)
    return ph

def validate_abg(ph, pco2, hco3):
        # if 10 ** (9-ph) - 24 * pco2/hco3 <= 0.1:  # 24*pco2/hco3 = [H+] in nmol & pH = -log[H+ in mol]
        #   return True
        # return False
    if abs(ph - calculatedph(pco2, hco3)) <= 0.3:
        return True
    else:
        return False


def is_abg_normal(ph, pco2, hco3):
    # According to the National Institute of Health, typical normal values are:
    # pH: 7.35-7.45
    # Partial pressure of oxygen (PaO2): 75 to 100 mmHg
    # Partial pressure of carbon dioxide (PaCO2): 35-45 mmHg
    # Bicarbonate (HCO3): 22-26 mEq/L
    # Oxygen saturation (O2 Sat): 94-100%
    if 7.35 <= ph <= 7.45 and 25 <= pco2 <= 45 and 22 <= hco3 <= 26:
        return True
    return False


def anion_gap(na, cl, hco3, albumin=4):
    return na - cl - hco3 + (4 - albumin) * 2.5  # albumin in mg/dl
    # todo correction for phosphate


def analysemetacidosis(na, cl, hco3, albumin=4):
    ag = anion_gap(na, cl, hco3, albumin) #ag normal is taken as 12 +/- 4 (Medscape)
    if 8 <= ag <= 16:
        return 1
    elif ag > 16:
        return 0
    else:
        return 2


def analyserespacidosis(hco3, pco2):
    ratio = abs(pco2 - 40) / 10
    if abs(hco3 - 24 - ratio) < abs(hco3 - 24 - 3.5*ratio):
        return 4
    else:
        return 5


def analyserespalkalosis(hco3, pco2):
    ratio = abs(pco2 - 40) / 10
    if abs(hco3 - 24 + 2*ratio) < abs(hco3 - 24 + 5*ratio):
        return 6
    else:
        return 7

def primary_disorder(ph, pco2, hco3, na, cl, albumin=4):
    #if any of the pCO2, hco3 or pH is abnormal, first we look at the pH --> whether acidic or alkaline.
    #if pH == 7.4 then either pCO2 or HCO3 must be abnormal i.e. beyond the normal range
    if ph < 7.4:
        if (24 - hco3)/24 >= (pco2 - 40)/40:
            # ag = anion_gap(na, cl, hco3, albumin)
            return analysemetacidosis(na, cl, hco3, albumin)
        else:
            return analyserespacidosis(hco3, pco2)
    elif ph > 7.4:
        if (hco3 - 24)/24 > (40 - pco2)/40:
            return 3
        else:
            return analyserespalkalosis(hco3, pco2)
    elif ph == 7.4:
        if hco3 < 22:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 26:
            return 3
        elif pco2 > 45:
            return analyserespacidosis(hco3, pco2)
        elif pco2 < 35:
            return analyserespalkalosis(hco3, pco2)
    else:
        return None


def secondarydisorder(na, cl, ph, pco2, hco3, albumin, primarydisorder=0):
    # returns the disorder & chronivity if it is applicable
    if ph == 7.4: #this part is assumptions
        if primarydisorder in [0,1,2]:
            return analyserespalkalosis(hco3,pco2)
        elif primarydisorder == 3:
            return analyserespacidosis(hco3, pco2)
        elif primarydisorder in [4,5]:
            return 3
        else:
            return analysemetacidosis(na, cl, hco3, albumin)
    elif primarydisorder in [0, 1, 2]:
        #ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        if pco2 < 1.5 * hco3 + 6:
            return analyserespalkalosis(hco3, pco2)
        elif pco2 > 1.5 * hco3 + 10:
            return analyserespacidosis(hco3, pco2)
        else:
            return None
    elif primarydisorder == 3:
        # ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        if pco2 < 0.7 * hco3 + 19:
            return analyserespalkalosis(hco3, pco2)
        elif pco2 > 0.7 * hco3 + 23:
            return analyserespacidosis(hco3, pco2)
        else:
            return None
    elif primarydisorder == 4: # Ac Resp. Acidosis. del(hco3) 1 - 1.5 per increase in ratio ***interpolation***
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 + ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + 1.5 * ratio:
            return 3
        else:
            return None
    elif primarydisorder == 5: # Chr. Resp. Acidosis --> 3 - 3.5
        #ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 + 3.0 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + 3.5 * ratio:
            return 3
        else:
            return None
    elif primarydisorder == 6: # Ac Resp alkalosis. 2 - 2.5
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 - 2.5 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 - 2 * ratio:
            return 3
        else:
            return None
    elif primarydisorder == 7:
        #ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 - 5 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 - 4 * ratio:
            return 3
        else:
            return None
    else:
        return None


def tertiarydisorder(hco3, primarydisorder, secondarydisorder, ag):
    if primarydisorder == 0 or secondarydisorder == 0:
        if hco3 == 24:
            deltaratio = 10 * (ag - 12) #assumption to look later for the effects. to avoid divide by zero lets make 14 - hco3 = 0.1
        else:
            deltaratio = (ag - 12) / (24 - hco3)
        #print("deltaratio: ", deltaratio)
        if deltaratio < 0.8:
            return 1
        elif deltaratio >= 2:
            return 3
        else:
            return None


def osmolargap(osm, na, bun, glucose):
    return osm - (2 * na + glucose / 18 + bun / 2.8)  # normal value < 10, values in mg/dl

def oxygenation(fio2, po2, pco2, age, patm=760, vp=47):
    hypoxia = None
    pf = po2/fio2
    if 200 < pf <= 300:
        hypoxia = " Mild Hypoxia"
    elif 100 < pf <= 200:
        hypoxia = " Moderate Hypoxia"
    elif pf <= 100:
        hypoxia = " Severe Hypoxia"
    alvartgrad = None
    aagrad = (patm - vp)*fio2 - 1.25 * pco2 - po2
    #print("po2:", po2)
    #print("pco2:", pco2)
    #print("fio2:", fio2)
    #print("age:", age)
    #print("patm:", patm)
    #print("vp:", vp)
    #print("aagrad:", aagrad)
    if aagrad > (age/4) + 4:
        alvartgrad = " With Raised A-a Gradient"
    else:
        alvartgrad = " With Normal A-a Gradient"
    if hypoxia is not None:
        return hypoxia + alvartgrad
    else:
        return None

def analyseabg(ph, po2, pco2, hco3, na, cl, age, fio2=0.21, patm=760, vp=47, albumin=4):
    ox = oxygenation(fio2=fio2, po2=po2, pco2=pco2, age=age, patm=patm, vp=vp)
    if validate_abg(ph,pco2,hco3) == False:
        return(["ABG is Inavalid"])
    elif is_abg_normal(ph, pco2, hco3) == True :
        if ox is None:
            return(["ABG is Normal"])
        else:
            return([ox])
    disorder = []
    p = primary_disorder(ph,pco2,hco3,na,cl,albumin)
    if p is not None:
        disorder.append('<p style= "color:blue"><strong>Primary Disorder:</strong></p>' + abnormalities[p])

    s = secondarydisorder(na, cl, ph, pco2, hco3, albumin, p)
    if s is not None:
        disorder.append('<p style= "color:blue"><strong>Secondary Disorder:</strong></p>' + abnormalities[s])
    ag = anion_gap(na, cl, hco3, albumin)
    t = tertiarydisorder(hco3, p, s, ag)
    if t is not None:
        disorder.append('<p style="color:blue><strong>Tertiary Disorder:</strong></p>' + abnormalities[t])

    if ox is not None:
        disorder.append('<p style= "color:blue"><strong>Oxygenation:</strong></p>' + ox)
    #print(disorder)
    return disorder

def getfio2(o2flowrate, deliverytype, venturicolorcode=None):
    if deliverytype == 0:
        return (4 * o2flowrate + 20) / 100
    elif deliverytype == 1:
        return (6 * o2flowrate - 1) / 100
    elif deliverytype == 2:
        return 1.0
    elif deliverytype == 3:
        if venturicolorcodes[venturicolorcode] == "Blue":
            return 0.24
        elif venturicolorcodes[venturicolorcode] == "White":
            return 0.28
        elif venturicolorcodes[venturicolorcode] == "Orange":
            return 0.31
        elif venturicolorcodes[venturicolorcode] == "Yellow":
            return 0.35
        elif venturicolorcodes[venturicolorcode] == "Red":
            return 0.4
        else:
            return 0.6
