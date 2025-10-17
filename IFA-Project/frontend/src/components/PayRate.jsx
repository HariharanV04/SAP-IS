import { Chip, Input, Select, SelectItem } from "@heroui/react";
import React, { useMemo, useState } from 'react'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@heroui/react";
import { Field, Form, Formik } from 'formik';
import { useEffect } from 'react';
import { useFetch } from '@services/ApiService';
import SelectDropdown from './SelectDropdown';

function PayRate({ data, setTaxData, setData, isTypeMulti = false, ...props }) {
    const { isOpen, onOpen, onClose, onOpenChange } = useDisclosure();
    const { fetchApi } = useFetch();
    const [loading, setLoading] = useState(false);
    const [taxTermsData, setTaxTermsData] = useState([]);
    const [selectedTaxTerms, setSelectedTaxTerms] = useState({})
    const inputProps = {
        ...props,
        isRequired: true,
        required: true,
        'aria-label': "payrate",
        'aria-labelledby': "payrate"
    }
    const [isSelected, setIsSelected] = useState(false);

    const handleChange = (key, e, setFieldValue) => {
        const value = e.target.value;
        setFieldValue(key, value)
    }

    const handleSubmit = (values) => {
        onClose()
        setData(values);
        setIsSelected(true);
    }

    const getData = async () => {
        setLoading(true);
        await fetchApi('/api/master/taxTerms').then(res => {
            // setTaxTermsData(res);
            const resData = res.length > 0 ? res.map(({ name, ...item }) => ({ label: name, key: item.id, value: item.id, ...item })) : []
            setTaxTermsData(resData)
        }).finally(() => {
            setLoading(false);
        })
    }

    useMemo(() => {
        if (data.type) {
            if (!isTypeMulti) {
                const filter = taxTermsData.filter(item => item.id == data.type);
                const selected = filter.length > 0 ? filter[0] : {};

                if (setTaxData) {
                    setTaxData(selected);
                }
                setSelectedTaxTerms(selected)
            }
            else {
                const filter = taxTermsData.filter(item => data.type.includes(item.id));

                if (setTaxData) {
                    setTaxData(filter);
                }
                setSelectedTaxTerms(filter)

            }
        }
    }, [taxTermsData, data.type])

    useEffect(() => {
        getData()
    }, [])


    useEffect(() => {
        if (data.min !== null) {
            setIsSelected(true);
        }
    }, [data]);

    /* const clearPayrate = () => {
        
    } */


    return (
        <>
            <Select
                {...props}
                selectedKeys={['0']}
                renderValue={() => {
                    return isSelected &&
                        <div className='flex items-center justify-between'>
                            <Chip color='primary' variant='flat' size='sm'>{data.min} - {data.max} {data.currency} per {data.duration} ({isTypeMulti ? (selectedTaxTerms.length > 0 && selectedTaxTerms.map(item => item.label).join(', ')) : selectedTaxTerms.label}) </Chip>
                            {/* <Button className='px-2 py-1 h-auto min-w-min' size='sm' onClick={clearPayrate}>X</Button> */}
                        </div>
                }}
                isOpen={false}
                onClick={() => onOpen()}
            >
                <SelectItem key={0} textValue={0}>0</SelectItem>
            </Select>

            <Modal
                isOpen={isOpen}
                placement='center'
                onOpenChange={onOpenChange}
                scrollBehavior="outside"
            >
                <ModalContent>
                    {(onClose) => (
                        <Formik
                            initialValues={data}
                            onSubmit={handleSubmit}
                        >
                            {({ values, setFieldValue }) => (
                                <Form>
                                    <>
                                        <ModalHeader className="flex flex-col gap-1">Pay Rate / Salary</ModalHeader>
                                        <ModalBody>
                                            <div className='grid grid-cols-11 gap-4'>
                                                <div className='col-span-12'>
                                                    <Field
                                                        name={'type'}
                                                        component={SelectDropdown}
                                                        path={'/master/taxTerms'}
                                                        optionsData={taxTermsData}
                                                        // setDropdownData={setTaxTermsData}
                                                        isMulti={isTypeMulti}
                                                    />
                                                </div>

                                                <Input
                                                    className='col-span-4'
                                                    type='number'
                                                    min={1}
                                                    {...inputProps}
                                                    placeholder='Min'
                                                    value={[values.min]}
                                                    required={false}
                                                    onChange={(e) => handleChange('min', e, setFieldValue)}
                                                />
                                                <Input
                                                    className='col-span-4'
                                                    type='number'
                                                    min={1}
                                                    {...inputProps}
                                                    placeholder='Max'
                                                    value={[values.max]}
                                                    isRequired={false}
                                                    required={false}
                                                    onChange={(e) => handleChange('max', e, setFieldValue)}
                                                />
                                                
                                                <Select
                                                    className='col-span-4'
                                                    {...inputProps}
                                                    name='currency'
                                                    isRequired
                                                    disallowEmptySelection
                                                    selectedKeys={[values.currency]}
                                                    onChange={(e) => handleChange('currency', e, setFieldValue)}
                                                >
                                                    <SelectItem key="USD">USD</SelectItem>
                                                    <SelectItem key="INR">INR</SelectItem>
                                                </Select>

                                                <Select
                                                    className='col-span-12'
                                                    {...inputProps}
                                                    name='duration'
                                                    selectedKeys={[values.duration]}
                                                    onChange={(e) => handleChange('duration', e, setFieldValue)}
                                                    isRequired
                                                    disallowEmptySelection
                                                >
                                                    <SelectItem key="Hourly">Hourly</SelectItem>
                                                    <SelectItem key="Daily">Daily</SelectItem>
                                                    <SelectItem key="Weekly">Weekly</SelectItem>
                                                    <SelectItem key="Bi-Weekly">Bi-Weekly</SelectItem>
                                                    <SelectItem key="Monthly">Monthly</SelectItem>
                                                    <SelectItem key="Yearly">Yearly</SelectItem>
                                                </Select>
                                            </div>
                                        </ModalBody>
                                        <ModalFooter>
                                            <Button color="danger" variant="light" onPress={onClose}>
                                                Close
                                            </Button>
                                            <Button color="primary" type='submit'>
                                                Apply
                                            </Button>
                                        </ModalFooter>
                                    </>
                                </Form>
                            )}
                        </Formik>
                    )}
                </ModalContent>
            </Modal >
        </>
    )
}

export default PayRate