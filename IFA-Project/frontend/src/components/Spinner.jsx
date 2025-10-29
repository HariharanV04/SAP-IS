import { Spinner as NextuiSpinner } from "@heroui/react"
import React from 'react'

function Spinner({isCentered = true, ...props}) {
    return (
        <div className={` ${isCentered && 'flex min-h-52 flex-1 justify-center items-center'}`}>
            <NextuiSpinner {...props} />
        </div>
    )
}

export default Spinner