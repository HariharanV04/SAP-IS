import { Button, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow } from '@heroui/react';
import { useFetch } from '@services/ApiService';
import React, { useState } from 'react'
import { toast } from 'sonner';

function ItemsTable(props) {
    const data = props.data ? props.data : []
    const columns = props.columns ? props.columns : [
        { name: 'ID', key: 'id' },
        { name: 'Type', key: 'type' }
    ]

    return (
        <>
            <Table
                isHeaderSticky
                isCompact
                isStriped
                className="max-h-[300px] overflow-y-auto"
                classNames={{
                    wrapper: 'p-0'
                }}
            >
                <TableHeader>
                    {
                        columns.map(item => (
                            <TableColumn key={item.key}>{item.name}</TableColumn>
                        ))
                    }
                </TableHeader>
                <TableBody items={data}>
                    {(item) => (
                        <TableRow key={item.id}>
                            {(columnKey) => <TableCell>{item[columnKey]}</TableCell>}
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </>
    )
}

function DeleteConfirmation({
    modal,
    deleteRecord,
    setDeleteRecord,
    titleKey = 'name',
    module = '',
    title = 'Confirm Delete?',
    api = null,
    apiMethod = 'DELETE',
    idKey = "id",
    refreshData = () => { },
    itemsColumns = null
}) {
    const { isOpen, onOpenChange, onClose } = modal;
    const [formLoading, setFormLoading] = useState(false);
    const [error, setError] = useState(null);
    const { fetchApi } = useFetch();

    const handleOpenChange = (e) => {
        onOpenChange(e)
        if (!e) {
            setDeleteRecord(null)
            setError(null)
        }
    }

    const handleDeleteAction = async () => {
        setFormLoading(true);
        await fetchApi(`${api}?id=${deleteRecord?.[idKey]}`, apiMethod).then(res => {
            if (res.success == true) {
                toast.success(res.message);
                setDeleteRecord(null);
                setError(null);
                onClose();
                refreshData();
            }
        }).catch((res) => {
            if (res.data.success == false) {
                setError(res.data);
            }
        }).finally(() => {
            setFormLoading(false);
        })
    }

    return (
        <>
            <Modal
                size='3xl'
                isOpen={isOpen}
                backdrop='blur'
                placement='center'
                onOpenChange={handleOpenChange}
                onClose={onClose}
            >
                <ModalContent>
                    {(onClose) => (
                        <>
                        {/* {JSON.stringify(deleteRecord)} */}
                            {
                                error == null &&
                                <>
                                    <ModalHeader className="flex flex-col gap-1">{title}</ModalHeader>
                                    <ModalBody>
                                        <div>
                                            You are about to delete <span className="font-semibold">{deleteRecord?.[titleKey]} ({deleteRecord?.[idKey]})</span> {module}, This action is irreversible.
                                        </div>
                                    </ModalBody>
                                    <ModalFooter>
                                        <Button variant="light" onPress={onClose}>
                                            Cancel
                                        </Button>
                                        <Button isLoading={formLoading} color="danger" onPress={handleDeleteAction}>
                                            Confirm Delete
                                        </Button>
                                    </ModalFooter>
                                </>
                            }

                            {
                                error?.success == false &&
                                <>
                                    <ModalHeader className="flex flex-col gap-1 mb-0 text-danger">Error while deleting "{deleteRecord?.[titleKey]} ({deleteRecord?.[idKey]})" {module}</ModalHeader>
                                    <ModalBody>
                                        <div>
                                            <div className="mb-2 font-semibold">{error.message}</div>

                                            <ItemsTable
                                                data={error.usedIn}
                                                columns={itemsColumns}
                                            />
                                        </div>
                                    </ModalBody>
                                    <ModalFooter>
                                        <Button variant="flat" onPress={onClose}>
                                            Close
                                        </Button>
                                    </ModalFooter>
                                </>
                            }
                        </>
                    )}
                </ModalContent>
            </Modal>
        </>
    )
}

export default DeleteConfirmation