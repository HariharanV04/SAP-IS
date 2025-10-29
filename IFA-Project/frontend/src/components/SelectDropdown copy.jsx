import { Autocomplete, AutocompleteItem, Chip, Select, SelectItem } from "@heroui/react";
import { useFetch } from '@services/ApiService';
import { formClass } from '@utils/classes';
import React, { useEffect, useState } from 'react'

function SelectDropdown({ renderChip, path, label = false, setDropdownData = false, labelKey, required = false, autocomplete = false, setFieldValue = false, ...restProps }) {

    const { fetchApi } = useFetch();
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const props = {
        isLoading,
        required,
        isRequired: required,
        ...restProps
    }

    const isMultiple = props.selectionMode == 'multiple';
    const getData = async () => {
        setIsLoading(true);
        await fetchApi(`/api${path}`).then(res => {
            setData(res)
            if (setDropdownData) {
                setDropdownData(res);
            }
        }).finally(() => {
            setIsLoading(false);
        })
    }

    if (isMultiple) {
        props.defaultSelectedKeys = props.value ? props.value : ""

       /*  const keyValue = props.value ? props.value : "";
        props.defaultSelectedKeys = keyValue;
        props.selectedKeys = keyValue; */
    }
    else {
        const keyValue = props.value ? props.value.toString() : "";
        props.selectedKeys = [keyValue];
        props.selectedKey = keyValue;
    }

    if (setFieldValue) {
        props.onSelectionChange = (value) => {
            const record = value ? data.filter(item => item.id == value.currentKey)[0] : null;
            setFieldValue(value, record)
        }
    }

    /* if (renderChip) {
        props.onSelectionChange = (value) => {
            console.clear();
            console.log(props.value);
        }
        props.renderValue = (items) => {
            const { setSelectedData, setDataKey } = renderChip;

            const handleRemoveChip = (id) => {
                const regex = new RegExp(`\\b${id},?|,?\\b${id}`, 'g');

                const currentValue = props.value;
                const newValue = currentValue.replace(regex, '').replace(/^,|,$/g, '');
                console.log(currentValue);

                // setSelectedData('languages_spoken', newValue)
            }

            return (
                <div className="flex flex-wrap gap-2">
                    {items.map((item) => {
                        return <Chip key={item.props.value} onClose={() => handleRemoveChip(item.props.value)}>{item.props.children}</Chip>
                    }
                    )}
                </div>
            );
        }
    } */


    useEffect(() => {
        getData()
    }, [path])



    return (
        <div>
            {
                label && <div className={formClass.label}>{label} {required && <span className={formClass.required}>*</span>}</div>
            }
            {
                autocomplete ?
                    <Autocomplete
                        classNames={{
                            selectorButton: "hidden"
                        }}
                        aria-label="Autocomplete Dropdown"
                        {...props}
                    >
                        {
                            data.map((item) => (
                                <AutocompleteItem key={item.id} value={item.id}>{labelKey ? item[labelKey] : item.name}</AutocompleteItem>
                            ))
                        }
                    </Autocomplete> :
                    <Select
                        aria-label="Dropdown"
                        {...props}
                    >
                        {
                            data.map((item) => (
                                <SelectItem key={item.id} value={item.id}>{labelKey ? item[labelKey] : item.name}</SelectItem>
                            ))
                        }
                    </Select>
            }
        </div>
    )
}

export default SelectDropdown
