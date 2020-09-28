# -*- coding: utf-8 -*-
"""
Functions and Methods used to make the evaluation of the X-Transformer predictions
for the CANTEMIST-CODING competition.

@author: André Neves
"""
import logging
import numpy as np

def calc_acc(test_labs, pred_labs):
    """Function to compute the Macro and Micro precision, recall and f-scores.
    @Requires:
        test_labs = list of lists containing the labels present in the test files
        pred_labs = list of lists containing the predicted labels
    @Ensures:
        mac_prec = macro precision
        mac_rec = macro recall
        mac_f1 = macro f1
        mic_prec = micro precision
        mic_rec = micro recall
        mic_f1  = micro f1
    """
    #For Macro-F1
    l_prec, l_recall, l_f1 = [], [], []
    
    #For Micro-F1
    l_TP, l_FP, l_FN = [], [], []
    
    for test, preds in zip(test_labs, pred_labs):
        TP = 0 #exists in test and in pred
        FP = 0 #exists in pred but not in test
        FN = 0 #exists in test but not in pred
        for l in preds:
            if l in test:
                TP+=1
            else:
                FP+=1
        for l in test:
            if l not in preds:
                FN+=1
        
        try:
            prec = TP / (TP+FP)
        except ZeroDivisionError:
            prec = 0
        
        try:    
            rec = TP / (TP+FN)
        except ZeroDivisionError:
            rec = 0
        
        try:
            f1 = 2*((prec*rec)/(prec+rec))
        except ZeroDivisionError:
            f1 = 0
            
        l_prec.append(prec)
        l_recall.append(rec)
        l_f1.append(f1)
        
        l_TP.append(TP)
        l_FP.append(FP)
        l_FN.append(FN)
    
    #macro
    try:
        mac_prec = sum(l_prec)/len(l_prec)
    except ZeroDivisionError:
        mac_prec = 0
    
    try:    
        mac_rec = sum(l_recall)/len(l_recall)
    except ZeroDivisionError:
        mac_rec = 0
        
    try:    
        mac_f1 = sum(l_f1)/len(l_f1)
    except ZeroDivisionError:
        mac_f1 = 0
    
    #micro
    try:
        mic_prec = sum(l_TP)/(sum(l_TP)+sum(l_FP))
    except ZeroDivisionError:
        mic_prec = 0
        
    try:
        mic_rec = sum(l_TP)/(sum(l_TP)+sum(l_FN))
    except ZeroDivisionError:
        mic_rec = 0
        
    try:
        mic_f1 = 2*((mic_prec*mic_rec)/(mic_prec+mic_rec))
    except ZeroDivisionError:
        mic_f1 = 0
        
    return mac_prec, mac_rec, mac_f1, mic_prec, mic_rec, mic_f1


def make_pred_list(l_probs, prob_min):
    """Generates the list of predictions based on a given threshold.
    @Requires: 
        l_probs = list of lists containing the labels predicted by X-Transformer and the
        corresponding confidence score for each label. list structure is:
            [[(label1, confidence_score1), (label2, confidence_score2), ... (labelN, confidence_scoreN)], [...],...]
        prob_min = minimum threshold value used to consider a prediction as valid or not.
    @Ensures:
        List of lists containing only the labels that have a confidence score >= prob_min.
    """
    l_pred_labs, l_aux = [], []
    for i in l_probs:
        for j in i:
            if j[1] > prob_min:
                l_aux.append(j[0])
                
        if len(l_aux) == 0: #if empty, stores the one with the highest probability
            l_aux.append(i[0][0])

        l_aux.sort()
        l_pred_labs.append(l_aux)
        l_aux = []
            
    return l_pred_labs
    
    
def check_prob_min(l_probs, l_test_labs):
    """Evaluates all threshold values from -0.99 to 1 in order to retrieve the threshold 
    value that achieves the highest scores in a given evaluation measure (precision, recall or f1)
    @Requires: 
        l_probs = list of lists containing the labels predicted by X-Transformer and the
        corresponding confidence score for each label. list structure is:
            [[(label1, confidence_score1), (label2, confidence_score2), ... (labelN, confidence_scoreN)], [...],...]
        l_test_labs = list of lists containing the labels present in the test files
    @Ensures:
        The confidence score values that achieves the highest precision, recall and f1-scores.
    """    
    p_max_p, p_max_r, p_max_f = 0, 0, 0
    f1_max, mi_f1_max = 0, 0
    prec_max, mi_prec_max = 0, 0
    rec_max, mi_rec_max = 0, 0

    print('Looking for the best confidence scores...') 
    logging.info('Looking for the best confidence scores...')
    #Finds the minimun probability that achieves better accuracy results
    #l_aux = []
    for p in np.arange(-0.99, 1, 0.01):
        print(p) #DEBUG
        logging.info(p)
        l_pred_labs = make_pred_list(l_probs, p)     
    
        #Calculates accuracy
        prec, rec, f1, mi_prec, mi_rec, mi_f1 = calc_acc(l_test_labs, l_pred_labs)

        if prec >= prec_max and mi_prec >= mi_prec_max:
            print('>>> prec superior <<<')
            print('prec anterior: ', prec_max)
            print('mi prec anterior: ', mi_prec_max)
            print('p anterior: ', p_max_p)
            prec_max = prec
            mi_prec_max = mi_prec
            p_max_p = p
            print('prec nova: ', prec_max)
            print('mi prec nova: ', mi_prec_max)
            print('p nova: ', p_max_p)
        if rec >= rec_max and mi_rec >= mi_rec_max:
            print('>>> rec superior <<<')
            print('rec anterior: ', rec_max)
            print('mi rec anterior: ', mi_rec_max)
            print('p anterior: ', p_max_r)
            rec_max = rec
            mi_rec_max = mi_rec
            p_max_r = p
            print('rec nova: ', rec_max)
            print('mi rec nova: ', mi_rec_max)
            print('p nova: ', p_max_r)
        if f1 >= f1_max and mi_f1 >= mi_f1_max:
            print('>>> f1 superior <<<')
            print('f1 anterior: ', f1_max)
            print('mi f1 anterior: ', mi_f1_max)
            print('p anterior: ', p_max_f)
            f1_max = f1
            mi_f1_max = mi_f1
            p_max_f = p
            print('f1 nova: ', f1_max)
            print('mi f1 nova: ', mi_f1_max)
            print('p nova: ', p_max_f)
    
    print('Best value for precision: ' + str(p_max_p))
    print('Best value for recall: ' + str(p_max_r))
    print('Best value for f1-score: ' + str(p_max_f))
    logging.info('Best value for precision: ' + str(p_max_p))
    logging.info('Best value for recall: ' + str(p_max_r))
    logging.info('Best value for f1-score: ' + str(p_max_f))
    return p_max_p, p_max_r, p_max_f
