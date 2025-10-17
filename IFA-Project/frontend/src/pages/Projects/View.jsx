import React, { useEffect, useState } from 'react'
import { projects } from './List'
import { useNavigate, useParams } from 'react-router-dom';
import { Button, Card, CardBody, CardHeader } from '@heroui/react';
import { Calendar, Plus, PlusCircle, User } from 'lucide-react';

function View() {
    const { id } = useParams()
    const [current, setCurrent] = useState({});
    const navigate = useNavigate()
    const [flowData, setFlowData] = useState([]);
    /* const flowData = [
        {
            id: 1,
            file_name: 'project1.zip',
            description: 'test description test description description test description',
            status: 'Completed',
            "created_by": "Astrid",
            "created_date": "2024-11-15",
        },
        {
            id: 2,
            file_name: 'project2.zip',
            description: 'test description test description description test description',
            status: 'In Progress',
            "created_by": "DevOps Team",
            "created_date": "2024-09-20",
        }
    ] */

    const statusColor = (status) => {
        return status === "Completed" ? ('text-green-500') :
            status === "In Progress" ? ('text-yellow-500') :
                ('text-blue-500')
    }

    useEffect(() => {
        const filtered = projects.filter(item => item.id == id)[0]
        setCurrent(filtered);

        if (filtered.jobs.length > 0) {
            setFlowData(filtered.jobs)
        }
    }, [id]);

    const FlowCard = ({ item }) => {
        return (
            <Card className='p-5 relative'>
                <div className="text-2xl font-semibold absolute right-5 top-5">{item.id <= 9 ? `0${item.id}` : item.id}</div>

                <div className={`text-sm mt-2 ${statusColor(item.status)}`}>{item.status}</div>

                <div className="flex items-end">
                    <div className='flex-1'>
                        <div className='text-lg font-semibold mt-2'>{item.job_name}</div>
                        <div className='text-sm mt-1 text-default-600'>{item.job_description}</div>
                    </div>
                    <div>
                        <Button onPress={() => navigate('flow')} color='primary' className='font-semibold' radius='full' size='sm'>View</Button>
                    </div>
                </div>
                <div className='text-sm text-default-500 flex items-center gap-1 mt-2 border-t pt-3 mt-3'>
                    <Calendar size={16} /> {item.created_on}
                    <User className='ms-2' size={16} /> {item.created_by}
                </div>
            </Card>
        )
    }


    return (
        <>
            <div className="flex justify-between items-center mb-5">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800 mb-1">
                        Flows
                    </h1>
                    <p className="text-gray-600">
                        {current?.project_name}
                    </p>
                </div>
                <div>
                    <Button color='primary'><Plus size={16} /> Create new Flow</Button>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-5">
                {
                    flowData.map(item => <FlowCard key={item.id} item={item} />)
                }

                <Card
                    classNames={{
                        header: 'px-5',
                        body: 'px-5',
                        footer: 'px-5'
                    }}
                    radius='sm'
                    isPressable
                    onPress={() => { }}
                >
                    <CardBody
                        className='flex gap-1 items-center justify-center'
                        style={{
                            height: 140
                        }}
                    >
                        <div className='flex flex-col items-center text-default-600'>
                            <PlusCircle className='mb-2' size={32} />
                            Create new Flow
                        </div>
                    </CardBody>
                </Card>
            </div>

        </>
    )
}

export default View