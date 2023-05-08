"""
Low-rank probability matrix estimator for discrete distributions

Author : Laurène David
"""

import numpy as np
import pandas as pd
from scipy.stats.contingency import crosstab



class Discrete:
    """Low-rank Bivariate Discrete Probability Estimation
    
    Parameters 
    ----------
    alpha : float, default 0.1
    Level of precision of matrix estimation

    
    Attributes
    ----------
    probability_matrix : np.ndarray of shape (d1,d2) with d1 : nbr of attributes of X1, d2 : nbr of attributes of X2
    Estimated probability matrix of the joint distribution of the data X=(X1,X2)

    """

    def __init__(self,alpha=0.1):
        self.alpha = alpha 
        self.probability_matrix = None


    def _compute_matrix(self,X=None,n=None,Y1=None,Y2=None,discrete_case=True):
        if discrete_case == True:
            n = X.shape[0]
            k, Y1 = crosstab(X[:int(len(X)/2),0], X[:int(len(X)/2),1])
            _, Y2 = crosstab(X[int(len(X)/2):,0], X[int(len(X)/2):,1])
            
            self.keys = k

        cstar = self.alpha/10 
        d = np.max(np.shape(Y1))
        Y1 = Y1/np.sum(Y1)
        Y2 = Y2/np.sum(Y2)

        if (n <= d * np.log(d)):
            return (Y1 + Y2) / 2
        
        p, q = np.sum(Y1, axis=1), np.sum(Y1, axis=0)
        res = np.zeros(np.shape(Y1))
        T = int(np.log(d) / np.log(2))

        for t in range(T + 1):
            if (t < T):
                I = np.argwhere((p <= 2**(-t)) & (p > 2**(-t - 1)))
            else:
                I = np.argwhere((p <= 2**(-t)))

            if len(I) > 0 :
                for u in range(T + 1):
                    if (u < T):
                        J = np.argwhere((q <= 2**(-u)) & (q > 2**(-u - 1)))
                    else:
                        J = np.argwhere(q <= 2**(-u))
                    
                    if len(J) > 0 :
                        M = np.zeros((len(I), len(J)))
                        row_indices = np.zeros(Y2.shape[0], dtype=bool)
                        row_indices[I] = True
                        col_indices = np.zeros(Y2.shape[1], dtype=bool)
                        col_indices[J] = True
                        M = Y2[row_indices, :][:, col_indices]

                        if (np.sum(M) < 2 * self.alpha * np.log(d) / (n * np.log(2))):
                            for i in range(len(I)):  # +1
                                for j in range(len(J)):
                                    res[I[i], J[j]] = Y2[I[i], J[j]]

                        else:
                            tau = np.log(d) * np.sqrt(cstar * 2**(1 - min(t, u)) / n)
                            U, s, Vh = np.linalg.svd(M)
                            l = len(s[s >= tau])
                            H = np.dot(U[:, :l] * s[:l], Vh[:l, :])
                    
                            for i in range(len(I)):  # +2
                                for j in range(len(J)):
                                    res[I[i], J[j]] = H[i, j]
        
        res[res<0.] = 0.
        
        if np.sum(res) == 0:
            return (Y1+Y2)/2
        
        return res/np.sum(res)


    
    def fit(self,X):
        '''
        Fit categorical dataset to discrete probability matrix estimator

        Parameters:
        ----

        X: nd.array of size (n_samples,2) 
        A numpy array with 2 categorical variables (int, float or str)

        
        return:
        ----
        self : object
        Returns the instance itself.

        '''

        if not isinstance(X, np.ndarray):
            raise TypeError(f"Input X should be a nd.array, not a {type(X)}")
        
        if X.shape[0] == 0:
            raise ValueError("X is an empty array")
        
        if X.shape[1] != 2:
            raise ValueError(f"Input X should have shape (nb_samples,2), not (nb_samples,{X.shape[1]})") 
        
        if self.alpha < 0:
            raise ValueError(f"alpha should be positive")
        
        if type(self.alpha) not in (int,float):
            raise ValueError(f"alpha should an int or float, not {type(self.alpha)}")  

        self.probability_matrix = self._compute_matrix(X=X,discrete_case=True)
        
        return self


    
    def sample(self, n_samples=1):
        """
        Sample discrete data with low_rank probability matrix P

        Parameters 
        -------   
        n_samples : int, default=1
        Number of samples to draw from distribution 

        
        Returns
        -------
        sample: nd.array of shape (n_samples,)
        Samples drawn from discrete distribution with probability matrix P
        

        """
        # Reshape probability_matrix
        P = self.probability_matrix
        nrow, ncol = P.shape
        p = P.flatten()
        
        # Sample 2D multinomial data with probability matrix
        samples = np.random.multinomial(n=1, pvals=p, size=n_samples).reshape((n_samples,nrow,ncol))
        samples = np.argwhere(samples==1)[:,1:]

        # Map values of samples to the labels of original data 
        dict_d1, dict_d2 = [dict(zip(np.arange(len(k)),k)) for k in self.keys]
        samples_ = np.array([[dict_d1[i],dict_d2[j]] for i,j in samples])

        
        return samples_





## Test of class discrete with dataset ##

# # Source of HairEyeColor dataset: https://www.kaggle.com/datasets/jasleensondhi/hair-eye-color
# path_data = r"C:\Users\LaurèneDAVID\Documents\Projects\Dimension_Reduction\HairEyeColor.csv"
# df = pd.read_csv(path_data)
# X = df[["Hair","Eye"]].to_numpy()

# model = Discrete(alpha=0.01)
# model.fit(X)
# print(model.probability_matrix)
