import { Button, Dropdown, DropdownItem, DropdownMenu, DropdownTrigger } from '@heroui/react'
import { ArrowDown01Icon } from 'hugeicons-react';
import React from 'react'

function QuickFilterDropdown({
    setColumnFilters = () => { },
    columnFilters = {},
    columnKey = '',
    allText = 'All',
    options = [],
    allOptionEnabled = true
}) {

    const handleQuickFilter = (value, filterKey) => {
        if (value !== 'all') {
            setColumnFilters((prevFilters) => ({
                ...prevFilters,
                [filterKey]: value
            }))
        }
        else {
            setColumnFilters((prevFilters) => {
                const newFilters = { ...prevFilters };
                delete newFilters[filterKey];
                return newFilters
            })
        }
    }
    return (
        <Dropdown>
            <DropdownTrigger>
                <Button endContent={<ArrowDown01Icon />} variant="flat">
                    {
                        columnFilters[columnKey] ? columnFilters[columnKey] : allText
                    }
                </Button>
            </DropdownTrigger>
            <DropdownMenu
                selectedKeys={columnFilters[columnKey] ? [columnFilters[columnKey]] : []}
                onAction={(value) => handleQuickFilter(value, columnKey)}
                selectionMode="single"
                disallowEmptySelection={true}
            >
                {
                    allOptionEnabled &&
                    <DropdownItem key="all">All</DropdownItem>
                }
                {
                    options.map(item => (
                        <DropdownItem key={item.value}>{item.label}</DropdownItem>
                    ))
                }
            </DropdownMenu>
        </Dropdown>
    )
}

export default QuickFilterDropdown;