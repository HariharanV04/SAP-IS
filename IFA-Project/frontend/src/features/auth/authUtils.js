import { useDispatch, useSelector } from 'react-redux';
import { setAuthToken, clearAuthToken } from './authSlice';
import { useNavigate } from 'react-router-dom';
import { DATA_USER } from '@utils/constants';

export const useAuthActions = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleAuthentication = (token) => {
        dispatch(setAuthToken(token));
        localStorage.setItem('authToken', token);
    };

    const handleLogout = () => {
        dispatch(clearAuthToken());
        localStorage.removeItem('authToken');
        navigate('/',{replace: true});
    };

    const checkAuth = () => {
        const token = localStorage.getItem('authToken');

        if (token) {
            dispatch(setAuthToken(token));
            return true;
        } else {
            dispatch(clearAuthToken());
            return false;
        }
    };

    return {
        handleAuthentication,
        handleLogout,
        checkAuth,
    };
};