import { Input, Select, SelectItem, RadioGroup, Radio, Textarea } from "@heroui/react";
import { Field, ErrorMessage, useFormikContext } from 'formik';
import SelectDropdown from './SelectDropdown';
import { formClass } from '@utils/classes';
import { useEffect } from 'react';

const commonProps = { variant: 'bordered', 'aria-label': 'ss', 'aria-labelledby': 'ssdsd' };

export const Label = ({ label, required }) => {
    return label && <div className={formClass.label}>{label} {required && <span className={formClass.required}>*</span>}</div>
}
const ErrorMsg = ({ name }) => <ErrorMessage name={name} component="div" className="text-red-500 text-xs" />

export const TextInput = ({ label, name, required = false, ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field name={name}>
            {({ field }) => <Input {...field} {...props} {...commonProps} />}
        </Field>
        <ErrorMsg name={name} />
    </>
);

export const SelectInput = ({ label, name, required = false, options = [], ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field name={name}>
            {({ field }) => (
                <Select disallowEmptySelection selectedKeys={[field.value]} {...props} {...commonProps} {...field} /* required={required} isRequired={required} */>
                    {options.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                    ))}
                </Select>
            )}

        </Field>
        <ErrorMsg name={name} />
    </>
);

export const DynamicSelect = ({ label, name, path, required = false, ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field
            name={name}
            component={SelectDropdown}
            path={path}
            {...props}
        />
        <ErrorMsg name={name} />
    </>
);

export const RadioInput = ({ label, name, required = false, options, ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field name={name}>
            {({ field }) => (
                <RadioGroup
                    {...commonProps}
                    {...props}
                    orientation="horizontal"
                    size="sm"
                    {...field}
                >
                    {options.map(option => (
                        <Radio className='me-1' key={option.value} value={option.value}>{option.label}</Radio>
                    ))}
                </RadioGroup>
            )}
        </Field>
        <ErrorMsg name={name} />
    </>
);

export const TextareaInput = ({ label, name, required = false, ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field name={name}>
            {({ field }) => <Textarea {...field} {...props} {...commonProps} />}
        </Field>
        <ErrorMsg name={name} />
    </>
);

export const RatingInput = ({ label, name, path, required = false, ...props }) => (
    <>
        <Label label={label} required={required} />
        <Field name={name}>
            {({ field }) => (
                <SelectDropdown
                    path={path}
                    {...field}
                    {...props}
                    {...commonProps}
                /* required={required}
                isRequired={required} */
                />
            )}
        </Field>
        <ErrorMsg name={name} />
    </>
);

export const getFieldErrorNames = (formikErrors) => {
    const transformObjectToDotNotation = (obj, prefix = '', result = []) => {
        Object.keys(obj).forEach((key) => {
            const value = obj[key]
            if (!value) return

            const nextKey = prefix ? `${prefix}.${key}` : key
            if (typeof value === 'object') {
                transformObjectToDotNotation(value, nextKey, result)
            } else {
                result.push(nextKey)
            }
        })

        return result
    }

    return transformObjectToDotNotation(formikErrors)
}

export const ScrollToFieldError = ({
    scrollBehavior = { behavior: 'smooth', block: 'center' },
}) => {
    const { submitCount, isValid, errors } = useFormikContext()

    useEffect(() => {
        if (isValid) return

        const fieldErrorNames = getFieldErrorNames(errors)
        if (fieldErrorNames.length <= 0) return

        const element = document.querySelector(
            `input[name='${fieldErrorNames[0]}']`
        ) || document.querySelector(
            `select[name='${fieldErrorNames[0]}']`
        ) || document.querySelector(
            `div[name='${fieldErrorNames[0]}']`
        )
        console.log(fieldErrorNames);
        if (!element) return

        // Scroll to first known error into view
        element.scrollIntoView(scrollBehavior)

        // Formik doesn't (yet) provide a callback for a client-failed submission,
        // thus why this is implemented through a hook that listens to changes on
        // the submit count.
    }, [submitCount]) // eslint-disable-line react-hooks/exhaustive-deps

    return null
}