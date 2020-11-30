# Authors: Soledad Galli <solegalli@protonmail.com>
# License: BSD 3 clause

from typing import List, Optional, Union

import pandas as pd
import scipy.stats as stats

from feature_engine.base_transformers import BaseNumericalTransformer
from feature_engine.variable_manipulation import _check_input_parameter_variables


class BoxCoxTransformer(BaseNumericalTransformer):
    """
    The BoxCoxTransformer() applies the BoxCox transformation to numerical
    variables.

    The BoxCox transformation implemented by this transformer is that of
    SciPy.stats:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boxcox.html

    The BoxCoxTransformer() works only with numerical positive variables (>=0,
    the transformer also works for zero values).

    A list of variables can be passed as an argument. Alternatively, the
    transformer will automatically select and transform all numerical
    variables.

    Parameters
    ----------
    variables : list, default=None
        The list of numerical variables that will be transformed. If None, the
        transformer will automatically find and select all numerical variables.

    Attributes
    ----------
    lambda_dict_ : dictionary
        The dictionary containing the {variable: best exponent for the BoxCox
        transformation} pairs. These are determined automatically.

    Methods
    -------
    fit
    transform
    fit_transform

    See Also
    --------
    scipy.stats.boxcox
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boxcox.html

    References
    ----------
    .. [1] Box and Cox. "An Analysis of Transformations". Read at a RESEARCH MEETING,
        1964.
        https://rss.onlinelibrary.wiley.com/doi/abs/10.1111/j.2517-6161.1964.tb00553.x
    """

    def __init__(
        self, variables: Union[None, int, str, List[Union[str, int]]] = None
    ) -> None:

        self.variables = _check_input_parameter_variables(variables)

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Learns the optimal lambda for the BoxCox transformation.

        Parameters
        ----------
        X : pandas dataframe of shape = [n_samples, n_features]
            The training input samples. Can be the entire dataframe, not just the
            variables to transform.

        y : pandas Series, default=None
            It is not needed in this transformer. You can pass y or None.

        Raises
        ------
         TypeError
            If the input is not a Pandas DataFrame
            If any of the user provided variables are not numerical
        ValueError
            If there are no numerical variables in the df or the df is empty
            If the variable(s) contain null values
            If some variables contain zero values

        Returns
        -------
        self
        """

        # check input dataframe
        X = super().fit(X)

        if (X[self.variables] < 0).any().any():
            raise ValueError(
                "Some variables contain negative values, try Yeo-Johnson "
                "transformation instead."
            )

        self.lambda_dict_ = {}

        for var in self.variables:
            _, self.lambda_dict_[var] = stats.boxcox(X[var])

        self.input_shape_ = X.shape

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the BoxCox transformation.

        Parameters
        ----------
        X : Pandas DataFrame of shape = [n_samples, n_features]
            The data to be transformed.

        Raises
        ------
        TypeError
            If the input is not a Pandas DataFrame
        ValueError
            If the variable(s) contain null values.
            If the dataframe not of the same size as that used in fit().
            If some variables contain negative values.

        Returns
        -------
        X : pandas dataframe
            The dataframe with the transformed variables.
        """

        # check input dataframe and if class was fitted
        X = super().transform(X)

        # check if variable contains negative numbers
        if (X[self.variables] < 0).any().any():
            raise ValueError(
                "Some variables contain negative values, try Yeo-Johnson "
                "transformation instead."
            )

        # transform
        for feature in self.variables:
            X[feature] = stats.boxcox(X[feature], lmbda=self.lambda_dict_[feature])

        return X
