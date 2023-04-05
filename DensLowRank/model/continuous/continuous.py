"""
Low-rank probability density function estimator for continuous distributions

Author : Laurène David 
"""

import numpy as np
import math
from DensLowRank.model.discrete.discrete import * #import Discrete parent class of Continuous (doesn't work ??)
from scipy.stats import beta, randint #to sample continuous data


class Continuous(Discrete):
    """Low-rank Bivariate Continuous Density Estimation
    
    Parameters 
    ----------
    alpha : float, default=0.1
    Level of precision of density estimation

    """

    L = 1
    
    def __init__(self,alpha=0.1):
        self.alpha = alpha 
        self.funs = None
    
    

    def _onedimensional_case(self,Z):
        ''' This function returns a density estimator for univariate continuous distributions.
        '''
        n = Z.shape[0]
        L = self.L

        r = np.min(Z[:int(n/2)])
        R = np.max(Z[:int(n/2)])

        if (R - r < n**(-1/3)*L**(-1/2)):
            return lambda x : 1/(R-r) if (x<=r and x>=R) else 0

        else:
            h = math.floor((R-r)*n**(1/3)*L**(1/2))**(-1)*(R-r)
            E = np.arange(-math.floor(r/h), math.ceil((1-r)/h-1))

            def f(x):
                N = np.zeros((len(E)+1,))
                for i in range(int(n/2)+1,n):
                    N[int((Z[i] - r)/h)] += 1
            
                return (1/h)*N[int((x-r)/h)]
        

        return f


    

    def fit(self,X):
        """
        Compute a probability density function estimator for bivariate continuous distributions.


        Parameters :
        ----------

        X : np.array of shape (n,2)
        A numpy array generated by a joint continuous distribution 


        Return :
        ---------
        density_estimator(x) : python function 
        A density function estimator for bivariate distributions 
        with input x as 2d np.array
    
    
        """

        if not isinstance(X, np.ndarray):
            raise TypeError(f"Input X should be a nd.array, not a {type(X)}")
        
        if X.shape[0] == 0:
            raise ValueError("X is an empty array")

        if self.alpha < 0:
            raise ValueError(f"alpha should be positive")
        
        if type(self.alpha) not in (int,float):
            raise TypeError(f"alpha should be a float, not {type(self.alpha)}")
        

        n = X.shape[0]
        L = self.L
        r1, R1 = np.min(X[:int(n/2),0]), np.max(X[:int(n/2),0])
        r2, R2 = np.min(X[:int(n/2),1]), np.max(X[:int(n/2),1])


        # Condition 1
        if R1 - r1 < n**(-1/3)*L**(-1/2):
            g = self._onedimensional_case(Z=X[int(n/2+1):,1])
            self.funs = lambda x,y : (1/(R1 - r1))*g(y) if (r1 <= x < R1) else 0 


        # Condition 2
        if R2 - r2 < n**(-1/3)*L**(-1/2):
            g = self._onedimensional_case(Z=X[int(n/2+1):,0])
            self.funs = lambda x,y : (1/(R2 - r2))*g(x) if (r2 <= y < R2) else 0 
  

        # Condition 3 
        h1 = math.floor((R1-r1)*n**(1/3)*L**(1/2))**(-1)*(R1-r1)
        h2 = math.floor((R2-r2)*n**(1/3)*L**(1/2))**(-1)*(R2-r2)
        
        E1 = np.arange(-math.floor(r1/h1),math.ceil((1-r1)/h1-1))
        E2 = np.arange(-math.floor(r2/h2),math.ceil((1-r2)/h2-1))
        
        N1 = np.zeros((len(E1)+1,len(E2)+1))
        N2 = np.zeros((len(E1)+1,len(E2)+1))

        for i,j in zip(range(int(n/2)+1, int(3*n/4)),range(int(3*n/4)+1, n)):
            x1, y1 = X[i,:]
            x2, y2 = X[j,:]
        
            N1[int((x1 - r1)/h1),int((y1 - r2)/h2)] = N1[int((x1 - r1)/h1),int((y1 - r2)/h2)] + 1
            N2[int((x2 - r1)/h1),int((y2 - r2)/h2)] = N2[int((x2 - r1)/h1),int((y2 - r2)/h2)] + 1

        P = super().fit(n=int(n/2), Y1=N1, Y2=N2, discrete_case=False)
        m1 = math.floor((R1-r1)*n**(1/3)*L**(1/2)) 
        m2 = math.floor((R2-r2)*n**(1/3)*L**(1/2))

        def f(x,y): 
            x1, y1 = int((x - r1)/h1), int((y - r2)/h2)
            if x1 < m1 and y1 < m2:
                return (1/h1*h2)*P[x1,y1]
            else:
                return (1/h1*h2)*(2/n)*(N1[x1,y1] + N2[x1,y1])
     
        self.funs = f
        return self
        


    def pdf(self,x,y):
        """
        Compute the estimated low-rank probability density function 

        Parameters 
        ---------
        x : nd.array 
        1D array 

        y : nd.array 
        1D array

        
        Return 
        ---------
        mat : nd.array of shape (len(x),len(y))
        Matrix with probability density values over support x and y

        """
        if np.any((x<0) & (x>1)):
            raise ValueError("The values in x should be between 0 and 1")
        
        if np.any((y<0) & (y>1)):
            raise ValueError("The values in y should be between 0 and 1")


        density_function = self.funs
        mat = np.zeros((len(x),len(y)))

        for i in len(x):
            for j in len(y):
                mat[i,j] = density_function(x[i],y[j])
        
        return mat
    



### Test Continuous model with continuous test data  

# def sample_continuous_data(n_samples,K):
#     samples = []
#     beta_distrib_1 = beta(a=1,b=2)
#     beta_distrib_2 = beta(a=2,b=2)

#     for i in range(n_samples):
#         uniform = randint(low=1,high=K).rvs()
#         X = beta_distrib_1.rvs()
#         Y = beta_distrib_2.rvs()
#         samples.append([X,Y])

#     return np.array(samples)

# n_samples = 10000
# K = 8
# samples = sample_continuous_data(n_samples,K)

# model = Continuous(alpha=0.1)
# model.fit(X=samples)

# x = np.linspace(0,1)
# x = np.linspace(0,1)
# density_funs = model.pdf(x,y) 

# print(density_funs)