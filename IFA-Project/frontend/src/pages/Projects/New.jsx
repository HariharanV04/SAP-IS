import { useState } from "react";
import { Button, DatePicker, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader, Select, SelectItem, Textarea } from "@heroui/react";
import { toast } from "sonner";
// import { Modal, Button, Input, Select, DatePicker } from "@heroui/react";

const sourcePlatform = ["Mulesoft"];
const targetPlatform = ["SAP Integration Suite"];

const New = ({ open, onClose }) => {
    const [projectName, setProjectName] = useState("");
    const [description, setDescription] = useState("");
    const [techStacks, setTechStacks] = useState([]);
    const [integrationType, setIntegrationType] = useState("");
    const [startDate, setStartDate] = useState("");
    const [loading, setLoading] = useState(false)
    const handleSubmit = () => {
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            onClose()
        }, 1000);
        // toast.error('')
    }

    return (
        <Modal isOpen={open} onClose={onClose}>
            <ModalContent>
                {(onClose) => (
                    <>
                        <ModalHeader>
                            <h2>Create New Project</h2>
                        </ModalHeader>
                        <ModalBody>
                            <Input
                                variant="bordered"
                                label="Project Name"
                                fullWidth
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                            />

                            <Input
                                variant="bordered"
                                label="Customer Name"
                                fullWidth
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                            />

                            <Select
                                variant="bordered"
                                label="Source Platform"
                                // selectionMode="multiple"
                                items={sourcePlatform.map((option) => ({ label: option, key: option }))}
                            /* selectedKeys={techStacks}
                            onSelectionChange={setTechStacks} */
                            >{(item) => <SelectItem>{item.label}</SelectItem>}</Select>

                            <Select
                                variant="bordered"
                                label="Target Platform"
                                items={targetPlatform.map((option) => ({ label: option, key: option }))}
                            /* selectedKeys={[integrationType]}
                            onSelectionChange={(keys) => setIntegrationType(keys.currentKey)} */
                            >{(item) => <SelectItem>{item.label}</SelectItem>}</Select>

                            <DatePicker
                                variant="bordered"
                                label="Start Date"
                            // value={startDate}
                            // onChange={(date) => setStartDate(date)}
                            />
                        </ModalBody>
                        <ModalFooter>
                            <Button variant="flat"  onPress={onClose}>
                                Close
                            </Button>
                            <Button isLoading={loading} color="primary" onPress={handleSubmit}>
                                Submit
                            </Button>
                        </ModalFooter>
                    </>
                )}

            </ModalContent>
        </Modal>
    );
};

export default New;
