import { Chip, Input, Select, SelectItem } from "@heroui/react";
import React, { useState } from 'react'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@heroui/react";
import { Form, Formik } from 'formik';
import { formClass } from '@utils/classes';
import SelectDropdown from './SelectDropdown';

function LocationPicker({ data, setData, ...props }) {
    const { isOpen, onOpen, onClose, onOpenChange } = useDisclosure();
    const inputProps = {
        ...props,
        'aria-label': "location",
        'aria-labelledby': "location"
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

    /* "city":"Mangalore",
    "state":"Karnataka",
    "country":"India",
    "zipcode":575028, */

    return (
        <>
            <Select
                {...props}
                selectedKeys={['0']}
                renderValue={() => {
                    return isSelected &&
                        <Chip color='primary' variant='flat' size='sm'>{data.city}   {data.zipcode} {data.state}, {data.country} </Chip>
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
                                        <ModalHeader className="flex flex-col gap-1">Location</ModalHeader>
                                        <ModalBody>
                                            <div className='grid grid-cols-12 gap-4'>
                                                <div className="col-span-6">
                                                    <SelectDropdown
                                                        label="Country"
                                                        name="country"
                                                        path='/master/skills'
                                                        required
                                                        selectedKeys={[values.country]}
                                                        {...inputProps}
                                                        onChange={(e) => handleChange('country', e, setFieldValue)}
                                                    />
                                                </div>
                                                <div className="col-span-6">
                                                    <SelectDropdown
                                                        label="State"
                                                        name="state"
                                                        path='/master/skills'
                                                        required
                                                        selectedKeys={[values.state]}
                                                        {...inputProps}
                                                        onChange={(e) => handleChange('state', e, setFieldValue)}
                                                    />
                                                </div>
                                                <div className="col-span-6">
                                                    <div className={formClass.label}>City</div>
                                                    <Input
                                                        {...inputProps}
                                                        value={[values.city]}
                                                        onChange={(e) => handleChange('city', e, setFieldValue)}
                                                    />
                                                </div>
                                                <div className="col-span-6">
                                                    <div className={formClass.label}>Zipcode</div>
                                                    <Input
                                                        {...inputProps}
                                                        value={[values.zipcode]}
                                                        onChange={(e) => handleChange('zipcode', e, setFieldValue)}
                                                    />
                                                </div>


                                                {/* <Select
                                                    className='col-span-3'
                                                    {...inputProps}
                                                    name='currency'
                                                    selectedKeys={[values.currency]}
                                                    onChange={(e) => handleChange('currency', e, setFieldValue)}
                                                >
                                                    <SelectItem key="USD">USD</SelectItem>
                                                    <SelectItem key="INR">INR</SelectItem>
                                                    <SelectItem key="CAD">CAD</SelectItem>
                                                </Select>
                                                <Input
                                                    className='col-span-4'
                                                    type='number'
                                                    min={1}
                                                    {...inputProps}
                                                    placeholder='Min'
                                                    value={[values.min]}
                                                    onChange={(e) => handleChange('min', e, setFieldValue)}
                                                />
                                                <Input
                                                    className='col-span-4'
                                                    type='number'
                                                    min={1}
                                                    {...inputProps}
                                                    placeholder='Max'
                                                    value={[values.max]}
                                                    onChange={(e) => handleChange('max', e, setFieldValue)}
                                                />
                                                <Select
                                                    className='col-span-4'
                                                    {...inputProps}
                                                    name='duration'
                                                    selectedKeys={[values.duration]}
                                                    onChange={(e) => handleChange('duration', e, setFieldValue)}
                                                >
                                                    <SelectItem key="Hourly">Hourly</SelectItem>
                                                    <SelectItem key="Daily">Daily</SelectItem>
                                                    <SelectItem key="Weekly">Weekly</SelectItem>
                                                    <SelectItem key="Bi-Weekly">Bi-Weekly</SelectItem>
                                                    <SelectItem key="Monthly">Monthly</SelectItem>
                                                    <SelectItem key="Yearly">Yearly</SelectItem>
                                                </Select>
                                                <Select
                                                    className='col-span-7'
                                                    {...inputProps}
                                                    selectedKeys={[values.type]}
                                                    onChange={(e) => handleChange('type', e, setFieldValue)}
                                                >
                                                    <SelectItem key="1099">1099</SelectItem>
                                                    <SelectItem key="Contract to Hire - C2C">Contract to Hire - C2C</SelectItem>
                                                    <SelectItem key="Contract To Hire - C2H">Contract To Hire - C2H</SelectItem>
                                                    <SelectItem key="Contract to Hire - W2">Contract to Hire - W2</SelectItem>
                                                    <SelectItem key="Independent Contractor/Consultant">Independent Contractor/Consultant</SelectItem>
                                                    <SelectItem key="India - Fulltime">India - Fulltime</SelectItem>
                                                    <SelectItem key="Part Time">Part Time</SelectItem>
                                                    <SelectItem key="Sub Contractor">Sub Contractor</SelectItem>
                                                    <SelectItem key="W2 - Contract">W2 - Contract</SelectItem>
                                                    <SelectItem key="W2 - Fulltime">W2 - Fulltime</SelectItem>
                                                </Select> */}
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

export default LocationPicker