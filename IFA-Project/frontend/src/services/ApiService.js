import { useAuthActions } from '@/features/auth/authUtils';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

let count = 0;
function restApiOptions(METHOD, PAYLOAD) {
    switch (METHOD) {
        case 'GET':
            return {
                params: PAYLOAD,
            };
        case 'POST':
        case 'PATCH':
            return {
                data: PAYLOAD,
            };
        case 'PUT':
            return {
                data: PAYLOAD,
            };
        case 'DELETE':
            return {
                data: PAYLOAD
            };
        default:
            return {
                params:PAYLOAD ,
            };
    }
}

export function useFetch() {
    const { authToken, ...rest } = useSelector((state) => state.auth);
    const { handleLogout } = useAuthActions();

    async function fetchApi(API, METHOD = 'GET', PAYLOAD = {}, headers = {}, restOptions = {}) {
        return new Promise((resolve, reject) => {
            try {
                axios({
                    method: METHOD,
                    url: API,
                    headers: {
                        'Authorization': !authToken ? null : `Bearer ${authToken}`,
                        ...headers
                    },
                    ...restOptions,
                    ...restApiOptions(METHOD, PAYLOAD),
                })
                    .then((res) => {
                        resolve(res.data);
                    })
                    .catch((err) => {
                        const response = err.response;
                        
                        const statusCode = response.status;

                        if (statusCode === 401) {
                            if (authToken) {
                                if (count === 0) {
                                    handleLogout();
                                    toast.error('Session Timedout!', { description: 'Your session has expired please login again.' })
                                }
                                count = count + 1;
                            }
                        } else if (statusCode == 500) {
                            //Handle 500
                        }


                        if (response?.data?.data?.message) {
                            toast.error(response.data.statusMessage, { description: response.data.data.message })

                            /* if (response.data?.data?.error !== undefined) {
                                console.error(response.data.data.error);
                            }
                            else {
                                console.error(response.statusText);
                            } */
                        }

                        else {
                            console.error('Error while performing this action, Please try again!')
                        }


                        

                        reject(response);

                    });
            } catch (error) {
                // console.error("Error in Promise, ", error);
                reject('System error. Please try again later!');
            }
        });
    }

    return { fetchApi };
}
