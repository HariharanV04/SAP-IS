import CustomCard from '@components/Card'
import { Button, Card, CardBody, CardFooter, CardHeader, Dropdown, DropdownItem, DropdownMenu, DropdownTrigger, Modal, useDisclosure } from '@heroui/react'
import { More01Icon, More02Icon } from 'hugeicons-react'
import { ArrowRight, BeakerIcon, Brush, Calendar, CheckCircleIcon, CircleAlert, CircleCheck, Clock, ClockIcon, Cog, Ellipsis, Plus, PlusCircle, User } from 'lucide-react'
import React from 'react'
import { useNavigate } from 'react-router-dom'
import New from './New'

export const projects = [
    {
        id: 1,
        project_name: "Product Demo Migration",
        customer: "Demo1 Corp",
        source_platform: "Mulesoft",
        target_platform: "SAP Integration Suite",
        status: "In Progress",
        created_date: "16-May-2025",
        created_by: "Deepan",
        jobs: [
            {
                job_id: 1,
                job_name: "Product Migration",
                job_description: "Demo Product Migration",
                file: "order_mapping.zip",
                status: "In Progress",
                created_on: "16-May-2025",
                created_by: "Deepan"
            }
        ]
    },

    {
        id: 2,
        project_name: "Inventory Sync Migration",
        customer: "Demo2 Corp",
        source_platform: "Mulesoft",
        target_platform: "SAP Integration Suite",
        status: "Draft",
        created_date: "16-May-2025",
        created_by: "Deepan",
        jobs: [
            {
                job_id: 2,
                job_name: "Inventory API Sync",
                job_description: "Convert Inventory API to BTP iFlow",
                file: "inventory_sync.zip",
                status: "Pending",
                created_on: "16-May-2025",
                created_by: "Deepan",
            }
        ]
    },

    {
        id: 3,
        project_name: "Payment Workflow Migration",
        customer: "Demo3 Corp",
        source_platform: "Mulesoft",
        target_platform: "SAP Integration Suite",
        status: "Draft",
        created_date: "16-May-2025",
        created_by: "Deepan",
        jobs: [
            {
                job_id: 3,
                job_name: "Payment Flow Automation",
                job_description: "Migrate and optimize payment logic",
                file: "payment_flow.zip",
                status: "Pending",
                created_on: "16-May-2025",
                created_by: "Deepan",
            }
        ]
    }
];

function List() {
    const navigate = useNavigate();
    const { onOpen, onClose, isOpen } = useDisclosure()
    const StatusIcon = ({ status }) => {
        return status === "Completed" ? (
            <CircleCheck className="h-5 w-5 text-green-500 mr-2" />
        ) : status === "In Progress" ? (
            <Clock className="h-5 w-5 text-yellow-500 mr-2" />
        ) : status === "Development" ? (
            <Cog className="h-5 w-5 text-blue-500 mr-2" />
        ) : status === "Design Phase" ? (
            <Brush className="h-5 w-5 text-red-500 mr-2" />
        ) : (
            <BeakerIcon className="h-5 w-5 text-purple-500 mr-2" />
        );
    }

    const handleCreateNewProject = () => {
        onOpen()
    }
    const ProjectCard = ({ project }) => {
        return (
            <Card
                classNames={{
                    header: 'px-5',
                    body: 'px-5',
                    footer: 'px-5'
                }}
                radius='sm'
            >
                <CardHeader className='flex justify-between items-center border-b-1'>
                    <div className="font-semibold text-lg">
                        {project.project_name} 
                        <span className="font-normal ps-2 text-xs text-default-500">(PROJ-{project.id})</span>
                    </div>
                    <Dropdown>
                        <DropdownTrigger>
                            <Button isIconOnly size='sm' variant='light'><Ellipsis /></Button>
                        </DropdownTrigger>
                        <DropdownMenu aria-label="Action event example" onAction={(key) => alert(key)}>
                            <DropdownItem key="edit">Edit</DropdownItem>
                            <DropdownItem key="delete" className="text-danger" color="danger">
                                Delete
                            </DropdownItem>
                        </DropdownMenu>
                    </Dropdown>
                </CardHeader>
                <CardBody className='flex flex-cols gap-1'>
                    {/* <p className="text-default-600 mb-3">{project.customer}</p> */}

                    <p className='mb-1'>Customer: <span className="font-medium">{project.customer}</span></p>
                    <div className="flex justify-between">
                        <p>Source Platform: <span className="font-medium">{project.source_platform}</span></p>
                        <p>Target Platform: <span className="font-medium">{project.target_platform}</span></p>
                    </div>
                    {/* <p>🔌 Integration Type: <span className="">{project.integration_type}</span></p> */}

                    <div className="flex items-center mt-5">
                        <StatusIcon status={project.status} />
                        <span className="font-medium">{project.status}</span>
                    </div>

                </CardBody>
                <CardFooter className='border-t-1 py-2 flex justify-between'>
                    <div className='text-sm text-default-500'>
                        Created on {project.created_date} by {project.created_by}
                    </div>
                    <Button onPress={() => navigate(`/projects/${project.id}`)}>Select <ArrowRight size={16} /></Button>
                </CardFooter>
            </Card>
        )
    }

    return (
        <>
            <div className="flex justify-between mb-5">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800 mb-1">
                        Projects
                    </h1>
                    <p className="text-gray-600">
                        List of available projects
                    </p>
                </div>
                <div>
                    <Button onPress={handleCreateNewProject} color='primary'><Plus size={16} /> Create new Project</Button>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-6">

                {projects.map((project, index) => (
                    <ProjectCard key={index} project={project} />
                ))}

                <Card
                    classNames={{
                        header: 'px-5',
                        body: 'px-5',
                        footer: 'px-5'
                    }}
                    radius='sm'
                    isPressable
                    onPress={handleCreateNewProject}
                >
                    <CardBody
                        className='flex gap-1 items-center justify-center'
                        style={{
                            height: 265
                        }}
                    >
                        <div className='flex flex-col items-center text-default-600'>
                            <PlusCircle className='mb-2' size={32} />
                            Create new Project
                        </div>
                    </CardBody>
                </Card>
            </div>

            {/* <Modal
                isOpen={isOpen}
                onClose={onClose}
            >
            </Modal> */}
            <New open={isOpen} onClose={onClose} />
        </>
    )
}

export default List