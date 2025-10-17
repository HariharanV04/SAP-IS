import React from 'react'
import logo from '@assets/logo.svg'
import { Outlet } from 'react-router-dom'
import { CREDIT_NAME } from '@utils/constants';
import loginBg from '@assets/login-graphic.png';
function PublicLayout() {
    const year = new Date().getFullYear();
    return (
        <>
            <div className="flex items-center h-screen">
                <div className="flex-none w-full md:w-1/3 px-20" style={styles.minWid}>
                    <img className='h-24 -ms-1 flex-none mb-14' src={logo} alt={CREDIT_NAME} />
                    <Outlet />
                </div>
                <div className="hidden md:block flex-1 h-screen" style={styles.publicBg}>
                    <div className="pt-10 px-20 text-5xl">
                        <div className="font-extralight">Integration,</div>
                        <div className="mt-2 font-medium italic">With Ease.</div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default PublicLayout


const styles = {
    publicBg: {
        background: `url(${loginBg}) right bottom no-repeat #d9e1e1`,
    },
    minWid: {
        minWidth: 500
    }
} 