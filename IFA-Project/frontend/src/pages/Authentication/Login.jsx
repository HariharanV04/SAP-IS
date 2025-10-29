import { Button, Checkbox, Input, Link } from "@heroui/react"
import React, { useEffect, useState } from 'react'
import { Formik, Form } from 'formik';
import { useAuthActions } from '@/features/auth/authUtils';
import { LockKeyIcon, Mail01Icon } from 'hugeicons-react';
import { useFetch } from '@services/ApiService';
import { toast } from 'sonner';

function Login() {
    const { handleAuthentication } = useAuthActions();
    const { fetchApi } = useFetch();
    const [loading, setLoading] = useState(false);
    const handleSubmit = async (values) => {
        setLoading(true)
        await fetchApi('/auth/login', 'POST', values).then(res => {
            handleAuthentication(res.accessToken);
            toast.dismiss();
            toast.success('Logged-In Successfully.', { duration: 800 })
        }).catch(err => {
            const errMsg = err.data.data.message;
            if (errMsg) {
                toast.error(errMsg)
            } else {
                toast.error('Error while logging in. Please check your credentials!')
            }
        }).finally(() => {
            setLoading(false);
        })
    }

    const handleContinue = () => {
        const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywiZW1haWwiOiJkZW1vQGl0cmVzb25hbmNlLmNvbSIsImZpcnN0X25hbWUiOiJEZW1vIiwibGFzdF9uYW1lIjoiSUQiLCJyb2xlX2lkIjoyLCJpYXQiOjE3NDcyMjY3ODgsImV4cCI6MTc0NzIzMzk4OH0.S-prd5Zzn_rZ-uPV_6gb36knBNOSNQoESz9NEM6cax4'
        handleAuthentication(token);
    }

    useEffect(() => {
        handleContinue();
    }, [])


    return (
        <>
            <div className='mt-5 md:text-4xl text-3xl font-semibold'>Welcome 👋</div>
            <div className="mt-2 text-lg text-slate-500">Please click here to continue</div>

            <Button onPress={handleContinue} isLoading={loading} type='submit' className='mt-5 font-semibold' size='lg' fullWidth color="primary">Continue to Portal</Button>
            {/* <Formik
                initialValues={{
                    email: '',
                    password: '',
                }}
                onSubmit={handleSubmit}
            >
                {({ values, setFieldValue }) => (
                    <Form>
                        <div className='mt-4 flex flex-1 flex-col gap-4 py-2'>
                            <Input
                                endContent={
                                    <Mail01Icon className="text-2xl text-default-400 pointer-events-none flex-shrink-0" />
                                }
                                name='email'
                                label="Email"
                                value={values.email}
                                placeholder="Enter your email"
                                color='primary'
                                variant="bordered"
                                onChange={(e) => setFieldValue('email', e.target.value)}
                            />
                            <Input
                                endContent={
                                    <LockKeyIcon className="text-2xl text-default-400 pointer-events-none flex-shrink-0" />
                                }
                                name='password'
                                label="Password"
                                placeholder="Enter your password"
                                type="password"
                                color='primary'
                                variant="bordered"
                                onChange={(e) => setFieldValue('password', e.target.value)}
                            />

                            <div className="flex py-2 px-1 justify-between">
                                <Checkbox
                                    classNames={{
                                        label: "text-small",
                                    }}
                                >
                                    Remember me
                                </Checkbox>
                                <Link color="secondary" href="/forgot-password" size="sm">
                                    Forgot password?
                                </Link>
                            </div>

                            <div className='flex justify-end'>
                                <Button isLoading={loading} type='submit' className='font-semibold' size='lg' fullWidth color="primary">Login</Button>
                            </div>
                        </div>
                    </Form>
                )}
            </Formik> */}
        </>
    )
}

export default Login