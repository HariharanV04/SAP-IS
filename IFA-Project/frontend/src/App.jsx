import React, { useEffect, useMemo } from 'react'
import PublicLayout from '@layouts/PublicLayout'
import { Route, Routes, useNavigate } from 'react-router-dom'
import { ForgotPassword, Login, ResetPassword } from '@pages/Authentication'
import { HeroUIProvider } from "@heroui/react"
import PrivateLayout from '@layouts/PrivateLayout';
import { useSelector } from 'react-redux';
import * as IFATool from '@pages/IFATool'
import * as APIDocs from '@pages/APIDocs'
import * as Projects from '@pages/Projects'
import * as Home from '@pages/Home'
import { useAuthActions } from '@/features/auth/authUtils'
import { Toaster } from 'sonner';
import { DATA_USER } from '@utils/constants'
import { LLMProviderProvider } from '@/contexts/LLMProviderContext'

function App() {
    const { checkAuth } = useAuthActions();
    const authToken = useSelector((state) => state.auth.authToken);
    const user = useSelector((state) => state.auth.user || {});
    const isDataOperator = user && user.role_id === DATA_USER;
    const navigate = useNavigate();

    useEffect(() => {
        if (!checkAuth()) {
            navigate('/')
        }
    }, [authToken])


    return (
        <LLMProviderProvider>
            <HeroUIProvider navigate={navigate} className='h-full'>
                <main className='h-full'>
                <Routes>
                    {
                        !authToken ?
                            <>
                                <Route path='/' element={<PublicLayout />}>
                                    <Route index element={<Login />} />
                                    <Route path='/forgot-password' element={<ForgotPassword />} />
                                    <Route path='/reset-password' element={<ResetPassword />} />
                                </Route>
                            </> :
                            <Route path='/' element={<PrivateLayout />}>
                                {/* <Route index element={<Home.View />} /> */}
                                <Route index element={<Projects.List />} />
                                <Route path='/api-docs' element={<APIDocs.View />} />
                                <Route path='/projects' element={<Projects.List />} />
                                <Route path='/projects/:id' element={<Projects.View />} />
                                <Route path='/projects/:id/flow' element={<IFATool.View />} />
                            </Route>
                    }

                    {/* <Route path='*' element={<Redirect />} /> */}
                </Routes>
                <Toaster
                    position='top-center'
                    toastOptions={{
                        classNames: {
                            error: 'bg-red-100 text-red-500',
                            success: 'bg-green-50 text-green-500',
                            warning: 'bg-yellow-50 text-yellow-500',
                            info: 'bg-blue-50 text-blue-400',
                        },
                    }}
                />
                </main>
            </HeroUIProvider>
        </LLMProviderProvider>
    )
}

export default App