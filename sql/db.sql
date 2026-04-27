ALTER TABLE IF EXISTS public.core_contract
ADD CONSTRAINT core_contract_driver_id_a0e596da_fk_core_driver_id FOREIGN KEY 
(driver_id)
    REFERENCES public.core_driver (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;
    
CREATE INDEX IF NOT EXISTS core_contract_driver_id_a0e596da
    ON public.core_contract(driver_id);

ALTER TABLE IF EXISTS public.core_contract
ADD CONSTRAINT core_contract_vehicle_id_4b024a04_fk_core_vehicle_id FOREIGN KEY 
(vehicle_id)
    REFERENCES public.core_vehicle (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_contract_vehicle_id_4b024a04
    ON public.core_contract(vehicle_id);

ALTER TABLE IF EXISTS public.core_notification
ADD CONSTRAINT core_notification_related_contract_id_555a98eb_fk_core_cont FOREIGN 
KEY (related_contract_id)
    REFERENCES public.core_contract (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_notification_related_contract_id_555a98eb
    ON public.core_notification(related_contract_id);

ALTER TABLE IF EXISTS public.core_notification
ADD CONSTRAINT core_notification_related_driver_id_0086e0e9_fk_core_driver_id FOREIGN 
KEY (related_driver_id)
    REFERENCES public.core_driver (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_notification_related_driver_id_0086e0e9
    ON public.core_notification(related_driver_id);

ALTER TABLE IF EXISTS public.core_notification
ADD CONSTRAINT core_notification_related_payment_id_b02abda0_fk_core_paym FOREIGN 
KEY (related_payment_id)
    REFERENCES public.core_payment (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_notification_related_payment_id_b02abda0
    ON public.core_notification(related_payment_id);

ALTER TABLE IF EXISTS public.core_notification
ADD CONSTRAINT core_notification_related_vehicle_id_2b727a6e_fk_core_vehi FOREIGN 
KEY (related_vehicle_id)
    REFERENCES public.core_vehicle (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_notification_related_vehicle_id_2b727a6e
    ON public.core_notification(related_vehicle_id);

ALTER TABLE IF EXISTS public.core_payment
ADD CONSTRAINT core_payment_contract_id_c4b3c11d_fk_core_contract_id FOREIGN KEY 
(contract_id)
    REFERENCES public.core_contract (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_payment_contract_id_c4b3c11d
    ON public.core_payment(contract_id);

ALTER TABLE IF EXISTS public.core_repair
ADD CONSTRAINT core_repair_driver_id_ad5bc3ba_fk_core_driver_id FOREIGN KEY 
(driver_id)
    REFERENCES public.core_driver (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_repair_driver_id_ad5bc3ba
    ON public.core_repair(driver_id);

ALTER TABLE IF EXISTS public.core_repair
ADD CONSTRAINT core_repair_vehicle_id_0d864abe_fk_core_vehicle_id FOREIGN KEY 
(vehicle_id)
    REFERENCES public.core_vehicle (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_repair_vehicle_id_0d864abe
    ON public.core_repair(vehicle_id);

ALTER TABLE IF EXISTS public.core_repairreceipt
ADD CONSTRAINT core_repairreceipt_repair_id_d77e187d_fk_core_repair_id FOREIGN KEY 
(repair_id)
    REFERENCES public.core_repair (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS core_repairreceipt_repair_id_d77e187d
    ON public.core_repairreceipt(repair_id)