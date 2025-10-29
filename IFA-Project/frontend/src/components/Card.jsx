import React from 'react'
import { BreadcrumbItem, Breadcrumbs, Card, CardBody, CardFooter, CardHeader, Skeleton } from "@heroui/react"
import { Link, useNavigate } from 'react-router-dom'
function CustomCard({ children, body = true, bodyClass="", headerClass="", footerClass="", isLoading = false, title = null, subtitle = null, footer = null, extra = null, breadcrumbs = [], ...restProps }) {
    const navigate = useNavigate();
    return (

        <Card shadow='sm' {...restProps}>
            {
                (title || extra) &&

                <CardHeader className={'px-8 flex justify-between item-center border-b ' + headerClass}>
                    <div>
                        <Skeleton isLoaded={!isLoading}>
                            {title && <div className='text-lg font-semibold'>{title}</div>}
                            {subtitle && <div className='text-sm'>{subtitle}</div>}
                            {
                                breadcrumbs.length > 0 &&
                                <Breadcrumbs>
                                    {
                                        breadcrumbs.map((item, idx) => (
                                            <BreadcrumbItem key={idx} onPress={() => navigate(item.link)}>
                                                {item.label}
                                            </BreadcrumbItem>
                                        ))
                                    }
                                    <BreadcrumbItem>{title}</BreadcrumbItem>
                                </Breadcrumbs>
                            }
                        </Skeleton>
                    </div>
                    <div>{extra && extra}</div>
                </CardHeader>
            }
            {
                body &&
                <CardBody className={'px-8 py-8 ' + bodyClass}>
                    <Skeleton isLoaded={!isLoading}>
                        {children}
                    </Skeleton>
                </CardBody>
            }

            {
                footer &&
                <Skeleton isLoaded={!isLoading}>
                    <CardFooter className={'px-8 border-t ' + footerClass}>
                        {footer}
                    </CardFooter>
                </Skeleton>
            }
        </Card>
    )
}

export default CustomCard
