import { CleanIcon, FilterIcon } from 'hugeicons-react'
import React, { useEffect, useState } from 'react'
import Drawer, { DrawerBody, DrawerFooter, DrawerHeader } from './Drawer'
import { Button, DateRangePicker, Input, Link, Radio, RadioGroup, Slider, table } from "@heroui/react"
import CreatableSelect from 'react-select/creatable';
import Select from 'react-select';
import { reactSelectProps } from './SelectDropdown';
import { Label } from './FormComponents';
import { I18nProvider } from '@react-aria/i18n';
import { fromDate, parseAbsoluteToLocal, parseDate, parseDateTime } from '@internationalized/date';
import ReactDatePicker from './ReactDatePicker';
import MaskedTextInput from "react-text-mask";
import dayjs from 'dayjs';
import { formClass } from '@utils/classes';

function TableFilters({ tableSorting = [], setPagination, isOpen, onClose, filters, setFilters, tableFilters, localFilterHandles = { enabled: false, fullData: [], setData: null } }) {
    const [tempFilters, setTempFilters] = useState({});
    const [selectedOperators, setSelectedOperators] = useState({});

    const handleColumnFilterChange = (columnKey, value) => {
        setTempFilters((prevFilters) => {
            return {
                ...prevFilters,
                [columnKey]: value
            }
        });
    };

    const handleLocalFilters = () => {
        const { fullData, setData } = localFilterHandles;
        if (fullData.length > 0) {
            const filteredData = [];
            if (Object.entries(filters).length > 0) {
                Object.entries(filters).map(([key, value]) => {
                    fullData.map(item => {
                        if (value.some(v => String(item[key]).toLowerCase().includes(String(v).toLowerCase()))) {
                            filteredData.push(item);
                        }
                    })
                })
                setData(filteredData)
            }
            else {
                setData(fullData)
            }
        }
    }

    const handleApplyFilters = () => {
        const cleanedObj = Object.fromEntries(
            Object.entries(tempFilters)
                // .filter(([key, value]) => value !== "" && value !== null && value !== 0 && (!Array.isArray(value)))
                .filter(([key, value]) => value && (!Array.isArray(value) || value.some(Boolean)))
                .map(([key, value]) => ([key, selectedOperators[key] ? `${selectedOperators[key]}=${value}` : value]))
            // .map(([key, value]) => ([key, (Array.isArray(tempFilters[key]) && tempFilters[key].length > 0) ? tempFilters[key].map(item => item.value) : value]))
        )
        /* console.log(tempFilters)
        console.log(cleanedObj)
        return */
        setFilters(cleanedObj);
        setPagination((prevValue) => ({
            ...prevValue,
            pageNumber: 1
        }));

        onClose()
    }

    const commonInputProps = {
        tabIndex: 1,
        size: "sm",
        labelPlacement: 'outside',
        variant: "bordered",
        className: "mt-2 w-full",
        placeholder: `Type here...`,
    }

    const handleOperatorChange = (e, key) => {
        setSelectedOperators((prevValues) => ({
            ...prevValues,
            [key]: e.target.value
        }))

    }

    const getInput = (item) => {

        const { title, key, type, options = [], isMulti = true, isExact = true, isFixedValue = false, ...restProps } = item;


        const itemProps = {
            ...commonInputProps,
            label: title,
            value: tempFilters[key] || "",
        }

        const LessGrterRadio = () => {
            return (
                <RadioGroup
                    className='me-3 relative z-0'
                    size='sm'
                    orientation="horizontal"
                    value={selectedOperators[key] ? selectedOperators[key] : '<'}
                    onChange={(e) => handleOperatorChange(e, key)}
                >
                    <Radio classNames={{ label: 'text-default-400 font-normal text-xs' }} size='sm' value="<">Less Than</Radio>
                    <Radio classNames={{ label: 'text-default-400 font-normal text-xs' }} size='sm' value=">">Greater Than</Radio>
                </RadioGroup>
            )
        }

        const selectProps = {
            isClearable: true,
            isMulti,
            components: {
                DropdownIndicator: null
            },
            placeholder: "Search here...",
            onChange: (newValue) => handleColumnFilterChange(key, newValue),
            value: tempFilters[key]
        }

        switch (true) {
            case type == 'slider':
                return (
                    <div className='flex justify-between'>
                        <Slider
                            {...itemProps}
                            classNames={{
                                value: 'font-semibold text-primary-400'
                            }}
                            getValue={(value) => (
                                <div className='flex items-center'>
                                    <LessGrterRadio />
                                    {value}
                                </div>
                            )}
                            onChange={(value) => handleColumnFilterChange(key, value)}
                            {...restProps}
                        />

                    </div>
                );

            case type == 'daterange':
                return (
                    <div>
                        {/* <I18nProvider locale="en-GB">
                            <DateRangePicker
                                {...itemProps}
                                classNames={{
                                    value: 'font-semibold text-primary-400'
                                }}
                                label={
                                    <div className='flex items-center justify-between'>
                                        {title}
                                        {
                                            tempFilters[`${key}_start`] &&
                                            <Link
                                                className='text-xs underline cursor-pointer hover:text-black select-none'
                                                onPress={() => {

                                                    handleColumnFilterChange(`${key}_start`, null)
                                                    handleColumnFilterChange(`${key}_end`, null);
                                                }}
                                            >
                                                Clear Selected
                                            </Link>
                                        }
                                    </div>
                                }
                                hideTimeZone
                                value={{
                                    start: tempFilters[`${key}_start`] ? parseDate(tempFilters[`${key}_start`]) : null,
                                    end: tempFilters[`${key}_end`] ? parseDate(tempFilters[`${key}_end`]) : null,
                                }}
                                onChange={(value) => {
                                    value?.start && handleColumnFilterChange(`${key}_start`, value.start.toLocaleString())
                                    value?.end && handleColumnFilterChange(`${key}_end`, value.end.toLocaleString());
                                }}
                                showMonthAndYearPickers
                            />
                        </I18nProvider> */}

                        <div className='text-sm mb-0.5 flex items-center justify-between'>
                            {title}
                            {
                                tempFilters[`${key}_start`] &&
                                <Link
                                    className='text-xs underline cursor-pointer hover:text-black select-none'
                                    onPress={() => {

                                        handleColumnFilterChange(`${key}_start`, null)
                                        handleColumnFilterChange(`${key}_end`, null);
                                    }}
                                >
                                    Clear Selected
                                </Link>
                            }
                        </div>

                        <ReactDatePicker
                            selectsRange={true}
                            startDate={tempFilters[`${key}_start`] ? new Date(tempFilters[`${key}_start`]) : null}
                            endDate={tempFilters[`${key}_end`] ? new Date(tempFilters[`${key}_end`]) : null}
                            onChange={(value) => {
                                handleColumnFilterChange(`${key}_start`, value[0] ? dayjs(value[0]).format("YYYY-MM-DD") : null);
                                handleColumnFilterChange(`${key}_end`, value[1] ? dayjs(value[1]).format("YYYY-MM-DD") : null);
                            }}
                            isClearable={true}
                            placeholderText="dd/mm/yyyy - dd/mm/yyyy"
                            customInput={
                                <MaskedTextInput
                                    type="text"
                                    mask={[
                                        /\d/, /\d/, "/", /\d/, /\d/, "/", /\d/, /\d/, /\d/, /\d/,
                                        " ", "-", " ",
                                        /\d/, /\d/, "/", /\d/, /\d/, "/", /\d/, /\d/, /\d/, /\d/
                                    ]}
                                    placeholder="dd/mm/yyyy - dd/mm/yyyy"
                                />
                            }
                        />
                    </div>
                );

            default:
                return (
                    <div>
                        <div className='text-sm mb-0.5'>{title}</div>
                        {
                            options.length > 0 ?
                                <Select
                                    options={options}
                                    {...selectProps}
                                    {...reactSelectProps}
                                    onChange={(newValue) => {
                                        if (newValue) {
                                            isMulti ?
                                                handleColumnFilterChange(key, newValue.map(item => item.value)) :
                                                handleColumnFilterChange(key, newValue.value)
                                        }
                                        else {
                                            handleColumnFilterChange(key, null)
                                        }
                                    }}
                                    value={tempFilters[key] && options.filter(option => tempFilters[key].includes(option.value))}
                                /> :
                                <CreatableSelect
                                    {...selectProps}
                                    noOptionsMessage={() => "Type something and press enter..."}
                                    formatCreateLabel={(value) => `Search "${value}"`}
                                    {...reactSelectProps}
                                    onChange={(newValue) => handleColumnFilterChange(key, newValue.map(item => item.value))}
                                    value={tempFilters[key] && Array.isArray(tempFilters[key]) ? tempFilters[key].map(item => ({ label: item, value: item })) : tempFilters[key]}
                                />
                        }
                    </div>
                );
        }
    }

    useEffect(() => {
        const defaultOperators = {}
        tableFilters.map(item => {
            if (item.isExact == false) {
                defaultOperators[item.key] = '<'
            }
        })
        setSelectedOperators(defaultOperators)
    }, [tableFilters])

    useEffect(() => {
        console.log('filters', filters)
        const cleanedObj = Object.fromEntries(
            Object.entries(filters)
                .filter(([key, value]) => value && (!Array.isArray(value) || value.some(Boolean)))
                .map(([key, value]) => (
                    [key, (Array.isArray(filters[key]) && filters[key].length > 0)
                        ? filters[key] // Keep the array intact without mapping to objects
                        : value.replace(/[<>=]/g, '')]
                ))
            // .map(([key, value]) => ([key, (Array.isArray(filters[key]) && filters[key].length > 0) ? filters[key].map(item => ({ label: item, key: item })) : value.replace(/[<>=]/g, '')]))
        )
        // console.log('filters', filters)
        setTempFilters(cleanedObj)
    }, [filters])


    useEffect(() => {
        localFilterHandles.enabled == true &&
            handleLocalFilters()
    }, [JSON.stringify(filters), localFilterHandles.fullData.length])



    return (
        <>
            <Drawer isOpen={isOpen} onClose={onClose}>
                <DrawerHeader><FilterIcon /> Filters</DrawerHeader>
                <DrawerBody>
                    {
                        tableFilters.filter(item => !item.onlySorting).map(item => getInput(item))
                    }
                </DrawerBody>
                <DrawerFooter>
                    <Button color="danger" variant="light" onPress={onClose}>
                        Close
                    </Button>
                    <Button color="primary" onClick={handleApplyFilters}>Apply Filters</Button>
                </DrawerFooter>
            </Drawer>
        </>
    )
}

export default TableFilters