import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function Redirect() {
    const navigate = useNavigate();
    useEffect(() => {
        navigate('/dashboard')
    }, [])

    return (
        <div>Loading...</div>
    )
}

export default Redirect