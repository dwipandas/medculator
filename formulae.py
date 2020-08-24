from math import log

abnormalities = ["High Anion Gap Metabolic Acidosis", "Normal Anion Gap Metabolic Acidosis",
                 "Low Anion Gap Metabolic Acidosis",
                 "Metabolic Alkalosis", "Acute Respiratory Acidosis", "Chronic Respiratory Acidosis",
                 "Acute respiratory Alkalosis", "Chronic Respiratory Alkalosis"]



def validate_abg(ph, pco2, hco3):
    if ph - (-log((24 * pco2) / (hco3 * 1000000000))) <= 0.1:  # 24*pco2/hco3 = [H+] in nmol & pH = -log[H+ in mol]
        return True
    return False


def is_abg_normal(ph, pco2, hco3):
    # According to the National Institute of Health, typical normal values are:
    # pH: 7.35-7.45
    # Partial pressure of oxygen (PaO2): 75 to 100 mmHg
    # Partial pressure of carbon dioxide (PaCO2): 35-45 mmHg
    # Bicarbonate (HCO3): 22-26 mEq/L
    # Oxygen saturation (O2 Sat): 94-100%
    if ph >= 7.35 and ph <= 7.45 and pco2 >= 35 and pco2 <= 45 and hco3 >= 22 and hco3 <= 26:
        return True
    return False


def anion_gap(na, cl, hco3, albumin=4):
    return na - cl - hco3 + (4 - albumin) * 2.5  # albumin in mg/dl
    # todo correction for phosphate


def analysemetacidosis(na, cl, hco3, albumin=4):
    ag = anion_gap(na, cl, hco3, albumin)
    if 10 <= ag <= 12:
        return 1
    elif ag > 12:
        return 0
    else:
        return 2


def analyserespacidosis(hco3, pco2):
    ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
    if abs(ratio - 1) < abs(ratio - 3.5):
        return 4
    else:
        return 5


def analyserespalkalosis(hco3, pco2):
    ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
    if abs(ratio - 2) < abs(ratio - 5):
        return 6
    else:
        return 7


def primary_disorder(ph, pco2, hco3, na, cl, albumin=4):
    if ph < 7.4:
        if hco3 < 24:
            # ag = anion_gap(na, cl, hco3, albumin)
            return analysemetacidosis(na, cl, hco3, albumin)
        else:
            return analyserespacidosis(hco3, pco2)
    elif ph > 7.4:
        if hco3 > 24:
            return 3
        else:
            return analyserespalkalosis(hco3, pco2)
    else:
        return None


def secondarydisorder(na, cl, ph, pco2, hco3, albumin, primarydisorder=0):
    # returns the disorder & chronivity if it is applicable
    if primarydisorder in [0, 1, 2]:
        ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
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
    elif primarydisorder == 4:
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 + ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + ratio:
            return 3
        else:
            return None
    elif primarydisorder == 5:
        ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        if hco3 < 24 + 3.5 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + 3.5 * ratio:
            return 3
        else:
            return None
    elif primarydisorder == 6:
        ratio = abs(pco2 - 40) / 10
        if hco3 < 24 + 2 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + 2 * ratio:
            return 3
        else:
            return None
    elif primarydisorder == 7:
        ratio = (abs(hco3 - 24) / (abs(pco2 - 40) / 10))
        if hco3 < 24 + 5 * ratio:
            return analysemetacidosis(na, cl, hco3, albumin)
        elif hco3 > 24 + 5 * ratio:
            return 3
        else:
            return None
    else:
        return None


def tertiarydisorder(hco3, primarydisorder, ag):
    if primarydisorder in [0, 1, 2]:
        deltaratio = (ag - 12) / (24 - hco3)
        if 0.4 <= deltaratio < 1:
            if ag > 10:
                return 1
            else:
                return 0
        elif deltaratio > 1:
            return 3
        else:
            return None


def osmolargap(osm, na, bun, glucose):
    return osm - (2 * na + glucose / 18 + bun / 2.8)  # normal value < 10, values in mg/dl

def oxygenation(fio2, po2, pco2, age, patm=760, vp=47):
    hypoxia = None
    if 60 < po2 < 80:
        hypoxia = " Mild Hypoxia"
    elif 40 < po2 < 60:
        hypoxia = " Moderate Hypoxia"
    elif po2 < 40:
        hypoxia = " Severe Hypoxia"
    alvartgrad = None
    aagrad = (patm - vp) - 1.25 * pco2 - po2
    if aagrad > (age/4) + 4:
        alvartgrad = " With Raised A-a Gradient"
    else:
        alvartgrad = " With Normal A-a Gradient"
    if hypoxia is not None:
        return hypoxia + alvartgrad
    else:
        return None

def analyseabg(ph, po2, pco2, hco3, na, cl, age, fio2=0.21, patm=760, vp=47, albumin=4):
    if validate_abg(ph,pco2,hco3) == False:
        return "ABG is Inavalid"
    elif is_abg_normal(ph, pco2, hco3) == True:
        return("ABG is Normal")
    disorder = []
    p = primary_disorder(ph,pco2,hco3,na,cl,albumin)
    if p is not None:
        disorder.append(abnormalities[p])

    s = secondarydisorder(na, cl, ph, pco2, hco3, albumin, p)
    if s is not None:
        disorder.append(abnormalities[s])
    ag = anion_gap(na, cl, hco3, albumin)
    t = tertiarydisorder(hco3, p, ag)
    if t is not None:
        disorder.append(abnormalities[t])
    ox = oxygenation(fio2, po2, pco2, age, patm, vp)
    if ox is not None:
        disorder.append(ox)
    #print(disorder)
    return disorder