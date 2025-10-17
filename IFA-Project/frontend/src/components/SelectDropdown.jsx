

import { useFetch } from '@services/ApiService';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';


export const reactSelectProps = {
    styles: {
        control: ({ borderWidth, borderRadius, borderColor, outline, boxShadow, ...baseStyles }, state) => {
            return { ...baseStyles, '&:hover': { borderColor: 'none' } }
        },
        option: (baseStyles, state) => ({
            ...baseStyles,
            cursor: state.isDisabled ? 'default' : 'pointer'
        }),
    },
    classNames: {
        control: ({ isDisabled, isFocused }) => `gap-3 text-default-400 text-small rounded-medium border-medium border-default-200 hover:border-default-400 focus:border-default-foreground`,
        menu: () => 'gap-1 p-1 outline-none box-border text-small bg-content1 rounded-large shadow-medium w-full p-1 overflow-hidden z-20',
        valueContainer: () => 'text-default-800',
        option: ({ isDisabled, isFocused, isSelected }) => {
            const classes = 'px-2 py-1.5 w-full rounded-small subpixel-antialiased cursor-pointer tap-highlight-transparent outline-none focus:z-10 focus:outline-2 focus:outline-focus focus:outline-offset-2 focus:dark:ring-offset-background-content1 hover:transition-colors hover:bg-default hover:text-default-foreground selectable:focus:bg-default selectable:focus:text-default-foreground'
            return `${classes} ${isSelected && 'bg-primary-400 text-white'} ${isSelected && 'bg-primary-400 text-white'}`
        },
    }
}

const SelectDropdown = ({ path, optionsData = [], field, form, isMulti = false, setDropdownData, labelKey, onValueChange }) => {
    const { fetchApi } = useFetch();
    const [isClearable, setIsClearable] = useState(false);
    const [isSearchable, setIsSearchable] = useState(true);
    const [isDisabled, setIsDisabled] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [options, setOptions] = useState([]);

    const commonProps = {
        ...reactSelectProps,
        isSearchable,
        isLoading,
        isDisabled
    }

    const getData = async () => {
        setIsLoading(true);
        await fetchApi(`/api${path}`).then(res => {
            const resData = res.length > 0 ? res.map(({ name, ...item }) => ({ label: labelKey ? item[labelKey] : name, key: item.id, value: item.id, ...item })) : []
            setOptions(resData)
            if (setDropdownData) {
                setDropdownData(resData);
            }
        }).finally(() => {
            setIsLoading(false);
        })
    }

    useEffect(() => {
        optionsData.length > 0 ? setOptions(optionsData) : getData();
    }, [path])

    const onChange = (option) => {
        form.setFieldValue(
            field.name,
            isMulti
                ? option.map((item) => item.value)
                : option.value
        );
        form.setFieldTouched(field.name, true);
    };

    const onBlur = (e) => {
        const selectedOption = options.filter(item => item.id == form.values[field.name]);
        
        if(onValueChange){
            onValueChange(selectedOption[0].value, selectedOption[0]);
        } 
    }

    const getValue = () => {
        if (options && field.value !== null) {
            return isMulti
                ? options.filter(option => field.value.indexOf(option.value) >= 0)
                : options.find(option => option.value === field.value);
        } else {
            return isMulti ? [] : '';
        }
    };

    return (
        <Select
            {...commonProps}
            {...field}
            value={getValue()}
            onChange={onChange}
            onBlur={onBlur}
            options={options}
            isMulti={isMulti}
        />
    );
};

export default SelectDropdown;
