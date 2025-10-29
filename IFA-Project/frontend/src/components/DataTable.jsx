import React, { useEffect } from "react";
import {
    Table,
    TableHeader,
    TableColumn,
    TableBody,
    TableRow,
    TableCell,
    Input,
    Button,
    DropdownTrigger,
    Dropdown,
    DropdownMenu,
    DropdownItem,
    User,
    Pagination,
    Spinner,
    Badge,
    Tooltip,
    Select,
    SelectItem,
} from "@heroui/react";
import { capitalize } from "@/utils";
import { ArrowDown01Icon, EnteringGeoFenceIcon, FilterIcon, FilterRemoveIcon, PlusSignIcon, Search01Icon, SortByDown01Icon, SortByDown02Icon, SortByUp01Icon, SortByUp02Icon } from "hugeicons-react";
import { useNavigate } from "react-router-dom";

export default function DataTable({ extraActions = null, sorting, setSorting, sortingColumns = [], statusKey = "job_status_name", tableProps = {}, columnFilters = {}, setColumnFilters, handleFilterOpen, searchable = true, columnControl = true, isPaginated = false, pagination=true, setPagination, onRowAction, addNewLink, loading = true, searchKey, columns, users, statusOptions, initialColumns }) {
    const navigate = useNavigate();
    const [filterValue, setFilterValue] = React.useState("");
    const [visibleColumns, setVisibleColumns] = React.useState(new Set(initialColumns));
    const [statusFilter, setStatusFilter] = React.useState([]);
    const [rowsPerPage, setRowsPerPage] = React.useState(pagination?.pageSize || 100);
    const [sortDescriptor, setSortDescriptor] = React.useState({
        column: "age",
        direction: "ascending",
    });
    const [page, setPage] = React.useState(pagination?.pageNumber || 1);
    const tableSorting = sortingColumns.length > 0 ? sortingColumns.filter(i => i.sorting) : []
    const hasSearchFilter = Boolean(filterValue);

    const headerColumns = React.useMemo(() => {
        if (visibleColumns === "all") return columns;

        return columns.filter((column) => Array.from(visibleColumns).includes(column.uid));
    }, [visibleColumns]);


    const filteredItems = React.useMemo(() => {
        let filteredUsers = [...users];

        if (hasSearchFilter) {
            filteredUsers = filteredUsers.filter((user) =>
                searchKey.some((key) =>
                    user[key].toLowerCase().includes(filterValue.toLowerCase())
                )
            );
        }

        if (Array.from(statusFilter).length > 0) {
            filteredUsers = filteredUsers.filter((user) =>
                Array.from(statusFilter).includes(user[statusKey]),
            );
        }


        return filteredUsers;
    }, [users, filterValue, statusFilter]);

    const pages = isPaginated ? Math.ceil(pagination.totalRecordCount / pagination.pageSize) : Math.ceil(filteredItems.length / rowsPerPage);

    const items = React.useMemo(() => {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        return !isPaginated ? filteredItems.slice(start, end) : filteredItems;
    }, [page, filteredItems, rowsPerPage]);

    const sortedItems = React.useMemo(() => {
        return [...items].sort((a, b) => {
            const first = a[sortDescriptor.column];
            const second = b[sortDescriptor.column];
            const cmp = first < second ? -1 : first > second ? 1 : 0;

            return sortDescriptor.direction === "descending" ? -cmp : cmp;
        });
    }, [sortDescriptor, items]);

    const renderCell = React.useCallback((user, columnKey, item) => {
        const filteredColumn = columns.filter(item => item.uid == columnKey)[0];
        const { type, classNames = '', colorMap, render = false, stack_key, stack_render } = filteredColumn ? filteredColumn : {};
        const cellValue = render ? render(user[columnKey], user) : user[columnKey];
        switch (type) {
            case "avatar":
                return (
                    <User
                        avatarProps={{ radius: "lg", src: user.avatar }}
                        description={user.email}
                        name={cellValue}
                    >
                        {user.email}
                    </User>
                );
            case "stack":
                return (
                    <div className="flex flex-col">
                        <p className={classNames}>{cellValue}</p>
                        <p className="text-bold text-tiny text-default-400">
                            {
                                stack_render ? stack_render(user[stack_key], user) : user[stack_key]
                            }
                        </p>
                    </div>
                );
            default:
                return <span className={classNames}>{cellValue}</span>;
        }
    }, [columns]);

    const onRowsPerPageChange = (e) => {
        if (setPagination) {
            setPagination((prevData) => ({
                ...prevData,
                pageNumber: 1,
                pageSize: Number(e.target.value)
            }))
            setRowsPerPage(Number(e.target.value));
        }
        else {
            setRowsPerPage(Number(e.target.value));
            setPage(1);
        }
    };

    const onSearchChange = React.useCallback((value) => {
        if (value) {
            setFilterValue(value);
            setPage(1);
        } else {
            setFilterValue("");
        }
    }, []);

    const onClear = React.useCallback(() => {
        setFilterValue("")
        setPage(1)
    }, [])

    const handleChangeSort = (key) => {
        setSorting(prevData => {
            const sameKey = prevData.order_by == key;
            return {
                order_by: key,
                order_type: sameKey && prevData.order_type == 'DESC' ? 'ASC' : 'DESC'
            }
        })
    }

    const topContent = React.useMemo(() => {
        return (
            <div className="flex flex-col gap-4">
                <div className="flex justify-between gap-3 items-end">
                    {
                        searchable &&
                        <Input
                            isClearable
                            className="w-full sm:max-w-[44%]"
                            placeholder="Search here..."
                            startContent={<Search01Icon />}
                            value={filterValue}
                            onClear={() => onClear()}
                            onValueChange={onSearchChange}
                        />
                    }
                    <div className="flex gap-3">
                        {
                            extraActions &&
                            extraActions
                        }
                        {
                            statusOptions.length > 0 &&
                            <Dropdown
                            >
                                <DropdownTrigger className="hidden sm:flex">
                                    <Button endContent={<ArrowDown01Icon className="text-small" />} variant="flat">
                                        Status
                                    </Button>
                                </DropdownTrigger>
                                <DropdownMenu
                                    classNames={{
                                        list: 'max-h-80 overflow-auto'
                                    }}
                                    // disallowEmptySelection
                                    closeOnSelect={false}
                                    selectedKeys={statusFilter}
                                    selectionMode="multiple"
                                    onSelectionChange={e => {
                                        console.log(e);
                                        setStatusFilter(e)
                                    }}
                                >
                                    {statusOptions.map((status) => (
                                        status.toggle !== false &&
                                        <DropdownItem key={status.uid} className="capitalize">
                                            {capitalize(status.name)}
                                        </DropdownItem>
                                    ))}
                                </DropdownMenu>
                            </Dropdown>
                        }
                        {
                            columnControl &&
                            <Dropdown>
                                <DropdownTrigger className="hidden sm:flex">
                                    <Button endContent={<ArrowDown01Icon className="text-small" />} variant="flat">
                                        Columns
                                    </Button>
                                </DropdownTrigger>
                                <DropdownMenu
                                    disallowEmptySelection
                                    aria-label="Table Columns"
                                    closeOnSelect={false}
                                    selectedKeys={visibleColumns}
                                    selectionMode="multiple"
                                    onSelectionChange={setVisibleColumns}
                                >
                                    {columns.map((column) => (
                                        column.toggle !== false &&
                                        <DropdownItem key={column.uid} className="capitalize">
                                            {capitalize(column.name)}
                                        </DropdownItem>
                                    ))}
                                </DropdownMenu>
                            </Dropdown>
                        }
                        {
                            addNewLink &&
                            <Button
                                onClick={() => navigate(addNewLink)}
                                color="primary"
                                endContent={<PlusSignIcon />}
                            >
                                Add New
                            </Button>
                        }
                        {
                            tableSorting.length > 0 &&
                            <Dropdown>
                                <Badge content={''} isInvisible={sorting.order_by == 'id'} color="primary">
                                    <DropdownTrigger className="hidden sm:flex">
                                        <Button endContent={<ArrowDown01Icon className="text-small" />} variant="flat">
                                            Sort By
                                        </Button>

                                    </DropdownTrigger>
                                </Badge>
                                <DropdownMenu
                                    disallowEmptySelection
                                    aria-label="Table Sort by"
                                    selectedKeys={new Set(sorting.order_by)}
                                    onAction={(e) => handleChangeSort(e)}
                                >
                                    {tableSorting.map((column) => (
                                        <DropdownItem
                                            key={column.key}
                                            className="capitalize"
                                        >
                                            <span className="flex items-center justify-between">
                                                {capitalize(column.title)}
                                                {
                                                    sorting.order_by == column.key &&
                                                    <span className="-mb-0.5">
                                                        {
                                                            sorting.order_type == 'DESC' ?
                                                                <SortByDown02Icon /> : <SortByUp02Icon />
                                                        }
                                                    </span>
                                                }
                                            </span>
                                        </DropdownItem>
                                    ))}
                                </DropdownMenu>
                            </Dropdown>
                        }

                        {
                            handleFilterOpen &&
                            <Badge content={Object.keys(columnFilters).length} color="primary">
                                <Button
                                    onClick={handleFilterOpen}
                                    variant="flat"
                                    isIconOnly
                                >
                                    <FilterIcon />
                                </Button>
                            </Badge>
                        }
                        {
                            Object.keys(columnFilters).length > 0 &&
                            <Tooltip content="Clear Filters">
                                <Button
                                    onClick={() => setColumnFilters({})}
                                    variant="flat"
                                    isIconOnly
                                >
                                    <FilterRemoveIcon />
                                </Button>
                            </Tooltip>
                        }
                    </div>
                </div>
            </div>
        );
    }, [
        filterValue,
        statusFilter,
        visibleColumns,
        onRowsPerPageChange,
        users.length,
        onSearchChange,
        hasSearchFilter,
    ]);

    const bottomContent = React.useMemo(() => {
        return (
            <div className="flex justify-between">
                <div className="flex justify-between items-center text-default-400 text-small">

                    <label className="flex items-center ">
                        Rows per page:
                        <select
                            className="bg-transparent border-1 rounded ms-2 outline-none"
                            onChange={onRowsPerPageChange}
                            value={rowsPerPage}
                        >
                            <option value={5}>5</option>
                            <option value={10}>10</option>
                            <option value={25}>25</option>
                            <option value={50}>50</option>
                            <option value={100}>100</option>
                        </select>
                    </label>

                    <span className=" ms-4">Total {isPaginated ? pagination.totalRecordCount : users.length} records</span>
                </div>

                <div className="flex items-center gap-5 py-2 px-2">
                    {
                        pages > 10 &&
                        <>
                            <Input
                                label="Page"
                                labelPlacement="outside-left"
                                className="w-32"
                                size="sm"
                                type="number"
                                min={1}
                                max={pages}
                                endContent={<EnteringGeoFenceIcon className="text-default-400" />}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        if (setPagination) {
                                            setPagination((prevData) => ({
                                                ...prevData,
                                                pageNumber: Number(e.target.value)
                                            }))
                                        }
                                        setPage(Number(e.target.value))
                                    }
                                }}
                            />
                        </>
                    }
                    {
                        !loading &&
                        <Pagination
                            isCompact
                            showControls
                            showShadow
                            color="primary"
                            page={setPagination ? pagination.pageNumber : page}
                            total={pages}
                            onChange={(number) => {
                                setPagination ? setPagination((prevData) => ({
                                    ...prevData,
                                    pageNumber: number
                                })) : setPage(number)
                            }}
                        />
                    }
                </div>
            </div>
        );
    }, [items.length, page, pages, hasSearchFilter, JSON.stringify(pagination)]);

    return (
        <Table
            aria-label="datatable"
            isHeaderSticky
            bottomContent={pagination && bottomContent}
            bottomContentPlacement="outside"
            classNames={{
                wrapper: "max-h-[382px]",
                tr: `even:bg-gray-100 rounded ${onRowAction ? "hover:bg-gray-200 cursor-pointer" : ""}`,
            }}
            sortDescriptor={sortDescriptor}
            topContent={topContent}
            topContentPlacement="outside"
            onSortChange={setSortDescriptor}
            removeWrapper
            isStriped={true}
            // onRowAction={onRowAction}
            {...tableProps}
        >
            <TableHeader columns={headerColumns}>
                {(column) => (
                    <TableColumn
                        {...column}
                        className={column.className ? column.className : ''}
                        key={column.uid}
                        allowsSorting={column.sortable}
                    >
                        {column.name}
                    </TableColumn>
                )}
            </TableHeader>
            <TableBody
                loadingContent={
                    <Spinner label="Loading..." />

                }
                isLoading={loading}
                emptyContent={"No records found"}
                items={sortedItems}
            >
                {(item) => (
                    <TableRow key={item.id}>
                        {(columnKey) => <TableCell onClick={() => { onRowAction && columnKey !== 'actions' && onRowAction(item) }}>{renderCell(item, columnKey)}</TableCell>}
                    </TableRow>
                )}
            </TableBody>
        </Table>
    );
}