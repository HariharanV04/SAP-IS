import React from "react"
import {
    Modal,
    ModalBody,
    ModalContent,
    ModalFooter,
    ModalHeader
} from "@heroui/react"

const Drawer = ({ children, ...props }) => {
    return (
        <>
            <Modal
                scrollBehavior="inside"
                placement="center"
                backdrop="opaque"
                size="full"
                classNames={{
                    wrapper: "flex justify-end",
                }}
                motionProps={{
                    variants: {
                        enter: {
                            x: 0,
                            opacity: 1,
                            transition: {
                                duration: 0.2,
                                ease: "easeOut",
                            },
                        },
                        exit: {
                            x: 50,
                            opacity: 0,
                            transition: {
                                duration: 0.1,
                                ease: "easeIn",
                            },
                        },
                    }
                }}
                className="rounded-md max-w-md w-full h-screen max-h-screen"
                {...props}
            >

                <ModalContent>
                    {children}
                </ModalContent>
            </Modal>
        </>
    )
}

export const DrawerHeader = ModalHeader
export const DrawerBody = ModalBody
export const DrawerFooter = ModalFooter

export default Drawer
