import React from 'react'
import DatePicker from 'react-datepicker';

function ReactDatePicker(props) {

    return (
        <DatePicker
            wrapperClassName='block w-full'
            className="p-2 w-full text-small rounded-medium border-medium border-default-200 hover:border-default-400 focus:border-default-foreground"
            dateFormat='dd/MM/yyyy'
            {...props}
        />
    )
}

export default ReactDatePicker