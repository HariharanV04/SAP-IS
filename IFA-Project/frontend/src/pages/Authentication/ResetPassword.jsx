import { Button, Checkbox, Input, Link } from "@heroui/react"
import React, { useState } from 'react'
import { Formik, Form } from 'formik';
import { useAuthActions } from '@/features/auth/authUtils';
import { LockKeyIcon, Mail01Icon } from 'hugeicons-react';
import { useFetch } from '@services/ApiService';
import { toast } from 'sonner';

function ResetPassword() {
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
            <div className='mt-5 md:text-4xl text-3xl font-semibold'>Email Sent!</div>
            <div className="mt-2 text-lg text-slate-500">Check your inbox for OTP.</div>
            <Formik
                initialValues={{
                    otp: '',
                    password: '',
                    confirm_password: '',
                }}
                onSubmit={handleSubmit}
            >
                {({ values, setFieldValue }) => (
                    <Form>
                        <div className='mt-4 flex flex-1 flex-col gap-4 py-2'>
                            <Input
                                classNames={{input: 'text-center text-xl font-semibold tracking-[0.35em]'}}
                                name='otp'
                                label="Enter OTP"
                                value={values.otp}
                                type='number'
                                size='lg'
                                variant="bordered"
                                labelPlacement='outside'
                                onChange={(e) => {
                                    e.target.value.length <= 6 &&
                                    setFieldValue('otp', e.target.value)
                                }}
                            />
                            

                            <div className='flex justify-end'>
                                <Button isLoading={loading} type='submit' className='font-semibold' size='lg' fullWidth color="primary">Verify OTP</Button>
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

export default ResetPassword