import { Button, Checkbox, Input, Link } from "@heroui/react"
import React, { useState } from 'react'
import { Formik, Form } from 'formik';
import { useAuthActions } from '@/features/auth/authUtils';
import { LockKeyIcon, Mail01Icon } from 'hugeicons-react';
import { useFetch } from '@services/ApiService';
import { toast } from 'sonner';

function ForgotPassword() {
    const { handleAuthentication } = useAuthActions();
    const { fetchApi } = useFetch();
    const [loading, setLoading] = useState(false);
    const handleSubmit = async (values) => {
        setLoading(true)
        /* await fetchApi('/auth/login', 'POST', values).then(res => {
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
        }) */

    }

    return (
        <>
            <div className='mt-5 md:text-4xl text-3xl font-semibold'>Forgot Password</div>
            <div className="mt-2 text-lg text-slate-500">Enter your email to reset your password.</div>
            <Formik
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

                            <div className='flex justify-end'>
                                <Button isLoading={loading} type='submit' className='font-semibold' size='lg' fullWidth color="primary">Submit</Button>
                            </div>

                            <div className="flex py-2 px-1 justify-center">
                                <Link color="secondary" href="/" size="sm">
                                    &larr; Back to login
                                </Link>
                            </div>
                        </div>
                    </Form>
                )}
            </Formik>
        </>
    )
}

export default ForgotPassword