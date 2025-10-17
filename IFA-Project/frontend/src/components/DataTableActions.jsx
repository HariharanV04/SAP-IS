import { Tooltip } from "@heroui/react"
import { Delete02Icon, Edit01Icon, Edit02Icon, EyeIcon, Link01Icon, PencilEdit01Icon, ViewIcon } from "hugeicons-react"
import { useNavigate } from "react-router-dom"

export const buttonClass = "text-lg cursor-pointer opacity-50 hover:opacity-100 active:opacity-50 "

export const ViewButton = ({ url, ...props }) => {
    const navigate = useNavigate();
    return (
        <Tooltip content="View Details">
            <span className={buttonClass + 'text-default-800'} onClick={() => navigate(`${url}`)} {...props}>
                <ViewIcon size={20} />
            </span>
        </Tooltip>
    )
}

export const EditButton = ({ onClick, url, ...props }) => {
    const navigate = useNavigate();
    return (
        <Tooltip content="Edit">
            <span className={buttonClass + 'text-default-800'} onClick={() => onClick ? onClick() : navigate(url)}  {...props} >
                <PencilEdit01Icon size={20} />
            </span>
        </Tooltip>
    )
}

export const LinkButton = ({ tooltip="Link", url, ...props }) => {
    const navigate = useNavigate();
    return (
        <Tooltip content={tooltip}>
            <a href={url} target="_blank" className={buttonClass + 'text-default-800'} {...props} >
                <Link01Icon size={20} />
            </a>
        </Tooltip>
    )
}

export const DeleteButton = ({ url, ...props }) => (
    <Tooltip color="danger" content="Delete">
        <span className={buttonClass + 'text-danger-600'} {...props}>
            <Delete02Icon size={20} />
        </span>
    </Tooltip>
)